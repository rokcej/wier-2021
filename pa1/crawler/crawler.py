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

USER_AGENT = "fri-ieps-mr"
SEED_URLS = [
    "http://gov.si",
    "http://evem.gov.si",
    "http://e-uprava.gov.si",
    "http://e-prostor.gov.si",
]
TIMEOUT = 2 # Selenium timeout
NUM_THREADS = 4


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


# List of tuples (url, from_page_id)
frontier = []
for seed_url in SEED_URLS:
    frontier.append((normalize_url(seed_url), None))

# Multi-threading
frontier_lock = threading.Lock()
thread_active = [True for _ in range(NUM_THREADS)]


def safe_pop(i):
    with frontier_lock:
        if len(frontier) > 0:
            return frontier.pop(i)
        return None

def safe_append(el):
    with frontier_lock:
        frontier.append(el)

def crawl(thread_id):
    print("==Thread " + str(threading.get_ident()) + " started==")

    driver = webdriver.Firefox()

    # Connect to DB
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True

    max_pages = 5
    while max_pages > 0:
        max_pages -= 1
        
        frontier_element = safe_pop(0)
        if frontier_element == None:
            thread_active[thread_id] = False
            if not any(thread_active):
                break
            time.sleep(0.1)
            continue
        thread_active[thread_id] = True

        # Get URL and domain
        url, from_page_id = frontier_element #frontier.pop(0)
        print("Processing URL: " + url)
        domain = urllib.parse.urlparse(url).netloc

        # Allow only *.gov.si
        if re.search(r"^(.+\.)?gov\.si$", domain) == None:
            print("Not *.gov.si URL")
            continue

        cur = conn.cursor()
        
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


        # Check robots.txt
        if robots != None:
            if not robots.can_fetch(USER_AGENT, url):
                print("Disallowed!")
                cur.close()
                continue

        # Check if page has been visited
        cur.execute("SELECT * FROM crawler.page WHERE url = %s", (url,))
        res = cur.fetchone()
        if res != None:
            print("Already visited page with same URL!")
            cur.close()
            continue

        # Get html
        try:
            driver.get(url)
            time.sleep(TIMEOUT)
        except:
            print("Error visiting URL!")
            cur.close()
            continue
        title = driver.title
        html = driver.page_source

        # Get html hash
        html_hash = str(hash(html))
        cur.execute("SELECT * FROM crawler.page WHERE html_hash = %s", (html_hash,))
        res = cur.fetchone()
        if res != None:
            print("Already visited page with same HTML content!")
            cur.close()
            continue

        # Get HTML status code
        response = requests.head(url, allow_redirects=True, headers={"User-Agent": USER_AGENT})
        http_status_code = response.status_code

        # Insert page into DB
        cur.execute("INSERT INTO crawler.page(site_id, url, html_content, html_hash, http_status_code, accessed_time)" +
            "VALUES (%s, %s, %s, %s, %s, now()) RETURNING id", (site_id, url, html, html_hash, http_status_code))
        page_id = cur.fetchone()[0]

        # Insert link into DB
        if from_page_id != None:
            cur.execute("INSERT INTO crawler.link(from_page, to_page) VALUES (%s, %s)", (from_page_id, page_id))

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
                #frontier.append((href_norm, page_id))
                safe_append((href_norm, page_id))
                
        cur.close()


    conn.close()

    driver.close()

    print("==Thread " + str(threading.get_ident()) + " finished==")



with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
    for i in range(NUM_THREADS):
        executor.submit(crawl, i)









# driver = webdriver.Firefox()

# # Connect to DB
# conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
# conn.autocommit = True


# max_pages = 200
# while len(frontier) > 0 and max_pages > 0:
#     max_pages -= 1
    
#     # Get URL and domain
#     url, from_page_id = frontier.pop(0)
#     print("Processing URL: " + url)
#     domain = urllib.parse.urlparse(url).netloc

#     # Allow only *.gov.si
#     if re.search(r"^(.+\.)?gov\.si$", domain) == None:
#         print("Not *.gov.si URL")
#         continue

#     cur = conn.cursor()
    
#     # Get site data
#     site_id = None
#     robots = None
#     cur.execute("SELECT * FROM crawler.site WHERE domain = %s", (domain,))
#     res = cur.fetchone()
#     if res == None:
#         # Insert site into DB
#         robots_content = curl("http://" + domain + "/robots.txt")
#         sitemap_content = None
        
#         if robots_content != None:
#             robots = urllib.robotparser.RobotFileParser()
#             robots.parse(robots_content.split('\n'))

#             sitemaps = robots.site_maps()
#             if sitemaps != None and len(sitemaps) > 0:
#                 sitemap_content = curl(sitemaps[0])
#             else:
#                 sitemap_content = curl("http://" + domain + "/sitemap.xml")

#         cur.execute("INSERT INTO crawler.site(domain, robots_content, sitemap_content) VALUES (%s, %s, %s) RETURNING id", (domain, robots_content, sitemap_content))
#         site_id = cur.fetchone()[0]
#     else:
#         # Fetch site from DB
#         robots_content = res[2]
#         if robots_content != None:
#             robots = urllib.robotparser.RobotFileParser()
#             robots.parse(robots_content.split('\n'))
#         site_id = res[0]


#     # Check robots.txt
#     if robots != None:
#         if not robots.can_fetch(USER_AGENT, url):
#             print("Disallowed!")
#             cur.close()
#             continue

#     # Check if page has been visited
#     cur.execute("SELECT * FROM crawler.page WHERE url = %s", (url,))
#     res = cur.fetchone()
#     if res != None:
#         print("Already visited page with same URL!")
#         cur.close()
#         continue

#     # Get html
#     try:
#         driver.get(url)
#         time.sleep(TIMEOUT)
#     except:
#         print("Error visiting URL!")
#         cur.close()
#         continue
#     title = driver.title
#     html = driver.page_source

#     # Get html hash
#     html_hash = str(hash(html))
#     cur.execute("SELECT * FROM crawler.page WHERE html_hash = %s", (html_hash,))
#     res = cur.fetchone()
#     if res != None:
#         print("Already visited page with same HTML content!")
#         cur.close()
#         continue

#     # Get HTML status code
#     response = requests.head(url, allow_redirects=True, headers={"User-Agent": USER_AGENT})
#     http_status_code = response.status_code

#     # Insert page into DB
#     cur.execute("INSERT INTO crawler.page(site_id, url, html_content, html_hash, http_status_code, accessed_time)" +
#         "VALUES (%s, %s, %s, %s, %s, now()) RETURNING id", (site_id, url, html, html_hash, http_status_code))
#     page_id = cur.fetchone()[0]

#     # Insert link into DB
#     if from_page_id != None:
#         cur.execute("INSERT INTO crawler.link(from_page, to_page) VALUES (%s, %s)", (from_page_id, page_id))

#     # Find all links
#     elems = driver.find_elements_by_xpath("//a[@href]")
#     for elem in elems:
#         href = elem.get_attribute("href")
#         if href != None:
#             href_norm = normalize_url(href)
#             if href_norm.startswith("mailto:"):
#                 continue
#             elif href_norm.startswith("tel:"):
#                 continue
#             frontier.append((href_norm, page_id))
            
#     cur.close()


# conn.close()

# driver.close()




# conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
# conn.autocommit = True
# cur = conn.cursor()
# cur.execute("INSERT INTO crawler.site(domain) VALUES ('test.com')")
# cur.execute("SELECT domain FROM crawler.site WHERE id = 1")
# value = cur.fetchone()[0]
# cur.close()
# conn.close()

