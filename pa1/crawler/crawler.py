from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
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
import signal
import sys
from bs4 import BeautifulSoup as BSHTML 
from pathlib import Path  

# Parameters
USER_AGENT = "fri-ieps-mr"
SEED_URLS = [
    "http://gov.si",
    "http://evem.gov.si",
    "http://e-uprava.gov.si",
    "http://e-prostor.gov.si",

    # "https://www.e-prostor.gov.si/fileadmin/DPKS/Transformacije_ETRS89/Aplikacije/ETRS89-SI.zip",
    # "https://egp.gu.gov.si/egp/",
    # "https://www.e-prostor.gov.si/fileadmin/DPKS/Transformacija_v_novi_KS/Aplikacije/3tra.zip",

]
MIN_WAIT_TIME = 2 # Selenium timeout
MAX_LOAD_TIME = 15
NUM_THREADS = 4
CRAWL_DELAY = 5


# Multi-threading
frontier_lock = threading.Lock()
history_lock = threading.Lock()
history = {}
thread_active = [True for _ in range(NUM_THREADS)]
is_running = True



def normalize_url(url):
    url_norm = url_normalize.url_normalize(url)
    # Remove "#"
    url_norm, url_frag = urllib.parse.urldefrag(url_norm)
    return url_norm

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
    
    with frontier_lock:
        # Check if URL already exists in page table
        cur.execute("SELECT id FROM crawler.page WHERE url = %s", (url,))
        res = cur.fetchone()
        if res != None:
            # If link doesn't exist yet, add it
            if from_page_id != None:
                cur.execute("SELECT * FROM crawler.link WHERE from_page = %s AND to_page = %s", (from_page_id, res[0]))
                if cur.fetchone() == None:
                    cur.execute("INSERT INTO crawler.link(from_page, to_page) VALUES (%s, %s)", (from_page_id, res[0]))
            return None
        # Insert URL into frontier
        cur.execute("INSERT INTO crawler.page(url, page_type_code, accessed_time) VALUES (%s, 'FRONTIER', now()) RETURNING id", (url,))
        res = cur.fetchone()
        if res == None:
            print("ERROR: Frontier append failed")
            return None
        page_id = res[0]
        if from_page_id != None:
            cur.execute("INSERT INTO crawler.link(from_page, to_page) VALUES (%s, %s)", (from_page_id, page_id))    
        #print("Added " + url + " to frontier.")
        return page_id

def crawl(thread_id, conn):
    print("===Thread " + str(thread_id) + " started===")

    f_info = open("info.log", "a")
    f_link = open("onclick.log", "a")

    # Create Selenium webdriver and set User-Agent
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", USER_AGENT)
    driver = webdriver.Firefox(profile)
    driver.set_page_load_timeout(MAX_LOAD_TIME)

    # Create DB connection cursor
    cur = conn.cursor()

    # Main loop
    max_pages = 5
    while is_running and max_pages > 0:
        # Get next element in frontier
        if not thread_active[thread_id]:
            time.sleep(0.5) # Add small delay while waiting
        with frontier_lock:
            # TODO Do both in only one SQL command if possible
            cur.execute("SELECT id, url FROM crawler.page WHERE page_type_code = 'FRONTIER' ORDER BY accessed_time ASC")
            res = cur.fetchone()
            if res != None:
                cur.execute("UPDATE crawler.page SET page_type_code = 'PROCESSING' WHERE id = %s", (res[0],))
            #print("Frontier pop result: " + str(res))
            frontier_element =  res

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

                sitemaps = None # robots.site_maps()
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

        # Check crawl delay
        with history_lock:
            if domain in history:
                last_time, crawl_delay = history[domain]
                curr_time = time.time()
                if curr_time - last_time > crawl_delay:
                    history[domain] = (curr_time, crawl_delay)
                else: # Add site to the back of the frontier
                    # print(f"Need to wait {curr_time - last_time} more seconds")
                    with frontier_lock:
                        cur.execute("UPDATE crawler.page " +
                        "SET page_type_code = 'FRONTIER', accessed_time = now() " +
                        "WHERE id = %s", (page_id,))
                    continue
            else:
                crawl_delay = CRAWL_DELAY
                if robots != None:
                    cd = robots.crawl_delay(USER_AGENT)
                    if cd != None:
                        crawl_delay = float(cd)
                history[domain] = (time.time(), crawl_delay)


        # Get html
        try:
            driver.get(url)
            time.sleep(MIN_WAIT_TIME)
        except:
            print(f"[{thread_id}] Error visiting URL!")
            with frontier_lock:
                # cur.execute("DELETE FROM crawler.link WHERE to_page = %s", (page_id,))    
                # cur.execute("DELETE FROM crawler.page WHERE id = %s", (page_id,))
                cur.execute("UPDATE crawler.page " +
                "SET site_id = %s, page_type_code = 'UNAVAILABLE', html_content = NULL, " +
                "html_hash = NULL, http_status_code = NULL, accessed_time = now() " +
                "WHERE id = %s", (site_id, page_id))
            continue
        html = driver.page_source
        page_type_code = 'HTML'

        # Get html hash
        html_hash = str(hash(html))
        cur.execute("SELECT id FROM crawler.page WHERE html_hash = %s", (html_hash,))
        res = cur.fetchone()
        duplicate_page_id = None
        if res != None: # Duplicate detected
            duplicate_page_id = res[0]
            print("Found a duplicate!")

        # Get HTTP status code
        try:
            response = requests.head(url, allow_redirects=True, headers={"User-Agent": USER_AGENT})
            http_status_code = response.status_code
        except Exception as e:
            print(f"[{thread_id}] Error getting URL HEAD!")
            print(e)
            http_status_code = None

        # Update page in DB
        if duplicate_page_id == None:
            cur.execute("UPDATE crawler.page " +
                "SET site_id = %s, page_type_code = %s, html_content = %s, " +
                "html_hash = %s, http_status_code = %s, accessed_time = now() " +
                "WHERE id = %s", (site_id, page_type_code, html, html_hash, http_status_code, page_id))
        else:
            cur.execute("UPDATE crawler.page " +
                "SET site_id = %s, page_type_code = 'DUPLICATE', html_content = NULL, " +
                "html_hash = NULL, http_status_code = %s, accessed_time = now() " +
                "WHERE id = %s", (site_id, http_status_code, page_id))
            cur.execute("INSERT INTO crawler.link(from_page, to_page) VALUES (%s, %s)", (page_id, duplicate_page_id))
            continue

        # Find all href links
        elems = driver.find_elements_by_xpath("//*[@href]")
        for elem in elems:
            href = elem.get_attribute("href")
            if href != None:
                href = urllib.parse.urljoin(url, href)
                href_norm = normalize_url(href)
                if href_norm.startswith("mailto:") or href_norm.startswith("tel:"):
                    f_info.write(href_norm + "\n")
                    continue
                frontier_append(cur, href_norm, page_id, robots)

        # Find all onclick links
        # document.location, self.location, window.location, location.href
        elems = driver.find_elements_by_xpath("//*[@onclick]")
        for elem in elems:
            onclick = elem.get_attribute("onclick")
            if onclick != None:
                f_link.write(onclick + "\n--------\n")
                # matches = re.findall(r"((document\.location)|(location\.href)|(self\.location)|(window\.location))(.|\n)*?(;|$)", onclick)
                matches = re.findall(r"(((document|window|self)\.location|location\.href)[^;]*)", onclick)
                for match in matches:
                    result = re.search("(\".*\")|('.*')|(`.*`)", match[0])
                    if result != None:
                        onclick_url = result.group()[1:-1]
                        onclick_url = urllib.parse.urljoin(url, onclick_url)
                        onclick_url_norm = normalize_url(onclick_url)

                        f_link.write(onclick_url_norm + "\n")

                        frontier_append(cur, onclick_url_norm, page_id, robots)
                f_link.write("\n\n")


        # Finding value of src
        soup = BSHTML(html, features="html.parser") 
        images = soup.findAll('img')
        image_id = None
        try:
            for image in images:
                src= image['src'] 
                iname= Path(src).name
                if  src.endswith(".jpg") ==True:
                    itype="image/jpg"                 
                elif src.endswith(".png")==True:
                    itype="png"                 
                elif src.endswith(".svg") ==True:
                    itype="svg"                   
                elif src.endswith(".gif")== True:
                    itype="gif"
               
                idata = requests.get(urllib.parse.urljoin(url,src))
                cur.execute("INSERT INTO crawler.image(page_id, filename, content_type,data,accessed_time) VALUES (%s, %s, %s, %s,now()) ", (page_id,iname,idata.headers["Content-Type"],idata.content))
        except:
            pass

    # Cleanup
    f_info.close()
    f_link.close()

    thread_active[thread_id] = False
    cur.close()
    driver.close()
    print("===Thread " + str(thread_id) + " finished===")


# def interrupt_handler(sig, frame):
#     global is_running
#     if is_running:
#         is_running = False
#         print("Interrupt received, stopping crawler...")
#         # while any(thread_active):
#         #     time.sleep(2)   
#         #     print("Waiting...")
#         # print("Bye.")


if __name__ == "__main__":
    # # Add interrupt handler
    # signal.signal(signal.SIGINT, interrupt_handler)

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

    # crawl(0, conn)

    conn.close()

