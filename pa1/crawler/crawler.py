from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import concurrent.futures
import threading
import url_normalize
import psycopg2
import urllib
import urllib.request
import urllib.robotparser
import requests
import hashlib
import time
import re

# Parameters
USER_AGENT = "fri-ieps-mr"
SEED_URLS = [
    "http://gov.si",
    "http://evem.gov.si",
    "http://e-uprava.gov.si",
    "http://e-prostor.gov.si",
]
TIMEOUT = 2 # Selenium timeout
NUM_THREADS = 4



# Multi-threading
frontier_lock = threading.Lock()
thread_active = [True for _ in range(NUM_THREADS)]



def normalize_url(url):
    url_normal = url_normalize.url_normalize(url)
    # TODO Remove #
    # r"#[\w\d]*$"
    return url_normal

def curl(url):
    try:
        res = requests.get(url, allow_redirects=True, headers={"User-Agent": USER_AGENT}, timeout=5)
        if res.status_code == 200:
            content_type = res.headers["Content-Type"]
            if content_type.startswith("text/") or content_type.startswith("application/xml"):
                return res.text
            else:
                f = open("./unsupported_content_type.log", "a")
                f.write(url + "\n" + content_type + "\n\n")
                f.close()
                print("Rejected robots.txt header type: " + res.headers['Content-Type'])
    except:
        return None
    return None

def frontier_pop_unsafe(cur):
    # Return tuple (page_id, url)
    #with frontier_lock:
    # TODO Do both in only one SQL command if possible
    cur.execute("SELECT id, url FROM crawler.page WHERE page_type_code = 'FRONTIER' ORDER BY id ASC")
    res = cur.fetchone()
    if res != None:
        cur.execute("UPDATE crawler.page SET page_type_code = 'PROCESSING' WHERE id = %s", (res[0],))
    #print("Frontier pop result: " + str(res))
    return res

def frontier_append(cur, url, from_page_id=None, robots=None):
    # Allow only *.gov.si
    domain = urllib.parse.urlparse(url).netloc # TODO Don't do this in 2 places
    if re.search(r"^(.+\.)?gov\.si$", domain) == None:
        #print("Not *.gov.si URL: " + url)
        return None

    # Check robots.txt
    if robots != None:
        if not robots.can_fetch(USER_AGENT, url):
            # print("Disallowed URL: " + url)
            return None
    
    with frontier_lock: # Is the lock needed?
        # Check if URL already exists in frontier
        cur.execute("SELECT id FROM crawler.page WHERE url = %s", (url,))
        if cur.fetchone() != None:
            return None
        # Insert URL into frontier
        cur.execute("INSERT INTO crawler.page(url, page_type_code) VALUES (%s, 'FRONTIER') RETURNING id", (url,))
        page_id = cur.fetchone()[0]
        if from_page_id != None:
            cur.execute("INSERT INTO crawler.link(from_page, to_page) VALUES (%s, %s)", (from_page_id, page_id))    
        #print("Added " + url + " to frontier.")
        return page_id

def crawl(thread_id, conn):
    print("===Thread " + str(thread_id) + " started===")

    # Create Selenium webdriver and set User-Agent
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", USER_AGENT)
    driver = webdriver.Firefox(profile)

    # Create DB connection cursor
    cur = conn.cursor()

    # Main loop
    max_pages = 30
    while max_pages > 0:
        # Get next element in frontier
        if not thread_active[thread_id]:
            time.sleep(0.5) # Add small delay while waiting
        with frontier_lock:
            frontier_element = frontier_pop_unsafe(cur)
            if frontier_element == None:
                thread_active[thread_id] = False
                if not any(thread_active):
                    break
                continue
            thread_active[thread_id] = True

        max_pages -= 1

        # Get URL and domain
        page_id, url = frontier_element
        print(f"[{thread_id}] Processing URL: " + url)
        domain = urllib.parse.urlparse(url).netloc
        
        # Get site data
        site_id = None
        robots = None
        cur.execute("SELECT * FROM crawler.site WHERE domain = %s", (domain,))
        res = cur.fetchone()
        if res == None:
            # Insert site into DB
            robots_content = curl("http://" + domain + "/robots.txt")
            sitemap_content = None
            
            if robots_content != None:
                robots = urllib.robotparser.RobotFileParser()
                robots.parse(robots_content.split('\n'))

                sitemaps = robots.site_maps()
                if sitemaps != None and len(sitemaps) > 0:
                    sitemap_content = curl(sitemaps[0])
                else:
                    sitemap_content = curl("http://" + domain + "/sitemap.xml")

            cur.execute("INSERT INTO crawler.site(domain, robots_content, sitemap_content) VALUES (%s, %s, %s) RETURNING id", (domain, robots_content, sitemap_content))
            site_id = cur.fetchone()[0]
        else:
            # Fetch site from DB
            robots_content = res[2]
            if robots_content != None:
                robots = urllib.robotparser.RobotFileParser()
                robots.parse(robots_content.split('\n'))
            site_id = res[0]

        # Get html
        try:
            driver.get(url)
            time.sleep(TIMEOUT)
        except:
            print(f"[{thread_id}] Error visiting URL!")
            with frontier_lock:
                cur.execute("DELETE FROM crawler.link WHERE to_page = %s", (page_id,))    
                cur.execute("DELETE FROM crawler.page WHERE id = %s", (page_id,))
            continue
        html = driver.page_source
        page_type_code = 'HTML'

        # Get html hash
        html_hash = str(hash(html))
        cur.execute("SELECT * FROM crawler.page WHERE html_hash = %s", (html_hash,))
        res = cur.fetchone()
        if res != None:
            page_type_code = 'DUPLICATE'

        # Get HTTP status code
        response = requests.head(url, allow_redirects=True, headers={"User-Agent": USER_AGENT})
        http_status_code = response.status_code

        # Update page in DB
        cur.execute("UPDATE crawler.page " +
            "SET site_id = %s, page_type_code = %s, html_content = %s, " +
            "html_hash = %s, http_status_code = %s, accessed_time = now() " +
            "WHERE id = %s", (site_id, page_type_code, html, html_hash, http_status_code, page_id))

        # Find all links
        elems = driver.find_elements_by_xpath("//a[@href]")
        for elem in elems:
            href = elem.get_attribute("href")
            if href != None:
                href_norm = normalize_url(href)
                if href_norm.startswith("mailto:"):
                    continue
                elif href_norm.startswith("tel:"):
                    continue
                frontier_append(cur, href_norm, page_id, robots)

    # Cleanup
    thread_active[thread_id] = False
    cur.close()
    driver.close()
    print("===Thread " + str(thread_id) + " finished===")


if __name__ == "__main__":
    # Connect to DB
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True

    # Add seed URLs to frontier
    if len(SEED_URLS) > 0:
        with conn.cursor() as cur:
            for seed_url in SEED_URLS:
                frontier_append(cur, seed_url, None, None)

    # Start the crawler
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        for i in range(NUM_THREADS):
            executor.submit(crawl, i, conn)

    conn.close()

