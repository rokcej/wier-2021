from selenium import webdriver
from seleniumwire import webdriver as wirewebdriver
from selenium.common.exceptions import TimeoutException
import concurrent.futures
import threading
import url_normalize
import psycopg2
import urllib
import urllib.request
import urllib.robotparser
import requests
import hashlib
import socket
import time
import re
import os
import signal
import sys

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
    # "https://www.umar.gov.si/fileadmin/user_upload/publikacije/kratke_analize/Strategija_dolgozive_druzbe/Strategija_dolgozive_druzbe.pdf"
]
NUM_THREADS = 6
CRAWL_DELAY = 5
SELENIUM_WAIT = 5 # Selenium minimum wait time
SELENIUM_TIMEOUT = 15 # Selenium maximum load time
REQUEST_TIMEOUT = 5 # Timeout for manual requests


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
        res = requests.get(url, allow_redirects=True, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
        if res.status_code == 200:
            content_type = None
            if "Content-Type" in res.headers:
                content_type = res.headers["Content-Type"]
            if content_type == None or content_type.startswith("text/") or content_type.startswith("application/xml"):
                return res.text
            else:
                f = open("./unsupported_content_type.log", "a")
                f.write(url + "\n" + content_type + "\n\n")
                f.close()
                print("Rejected robots.txt header type: " + res.headers['Content-Type'])
    except:
        return None
    return None

def frontier_append(cur, page_url, from_page_id=None, robots=None):
    # Allow only *.gov.si
    domain = urllib.parse.urlparse(page_url).netloc # TODO Don't do this in 2 places
    if re.search(r"^(.+\.)?gov\.si$", domain) == None:
        #print("Not *.gov.si URL: " + page_url)
        return None

    # Check robots.txt
    if robots != None:
        if not robots.can_fetch(USER_AGENT, page_url):
            # print("Disallowed URL: " + page_url)
            return None
    
    with frontier_lock:
        # Check if URL already exists in page table
        cur.execute("SELECT id FROM crawler.page WHERE url = %s", (page_url,))
        res = cur.fetchone()
        if res != None:
            # If link doesn't exist yet, add it
            if from_page_id != None:
                cur.execute("SELECT * FROM crawler.link WHERE from_page = %s AND to_page = %s", (from_page_id, res[0]))
                if cur.fetchone() == None:
                    cur.execute("INSERT INTO crawler.link(from_page, to_page) VALUES (%s, %s)", (from_page_id, res[0]))
            return None
        # Insert URL into frontier
        cur.execute("INSERT INTO crawler.page(url, page_type_code, accessed_time) VALUES (%s, 'FRONTIER', now()) RETURNING id", (page_url,))
        res = cur.fetchone()
        if res == None:
            print("ERROR: Frontier append failed")
            return None
        page_id = res[0]
        if from_page_id != None:
            cur.execute("INSERT INTO crawler.link(from_page, to_page) VALUES (%s, %s)", (from_page_id, page_id))    
        #print("Added " + page_url + " to frontier.")
        return page_id

def process_link(cur, page_id, page_url, robots, href, f_info, f_link, f_debug):
    # Check if link is mailto: or tel:
    if href.startswith("mailto:"):
        email = href[7:].split("?")[0]
        f_info.write(f"[EMAIL] {href}\n\t{email}\n")
        cur.execute("SELECT * FROM crawler.email WHERE email = %s", (email,))
        if cur.fetchone() == None:
            cur.execute("INSERT INTO crawler.email(email, page_id) VALUES (%s, %s)", (email, page_id))
        return
    elif href.startswith("tel:"):
        tel = href[4:]
        f_info.write(f"[TEL] {href}\n\t{tel}\n")
        cur.execute("SELECT * FROM crawler.tel WHERE tel = %s", (tel,))
        if cur.fetchone() == None:
            cur.execute("INSERT INTO crawler.tel(tel, page_id) VALUES (%s, %s)", (tel, page_id))
        return

    # Error check
    if href.find("mailto:") >= 0 or href.find("tel:") >= 0:
        f_info.write("[MAILTO ERROR] " + href + "\n")

    # Parse link
    href_parsed = urllib.parse.urlparse(href)
    href_path = href_parsed.path
    href_query = href_parsed.query
    # Check if link is a document
    data_exts = { ".pdf": "PDF",
        ".doc": "DOC", ".docx": "DOCX",
        ".ppt": "PPT", ".pptx": "PPTX",
        ".xls": "XLS", ".xlsx": "XLSX" }
    for data_ext in data_exts.keys():
        if href_path.lower().endswith(data_ext) or href_query.lower().endswith(data_ext):
            data_type_code = data_exts[data_ext]
            cur.execute("INSERT INTO crawler.page_data(page_id, data_type_code, data) VALUES (%s, %s, NULL) ", (page_id, data_type_code))
            return

    # Error check
    for data_ext in data_exts.keys():
        if href.lower().find(data_ext) >= 0:
            print(f"[DOC ERROR] {data_ext}: {href}")
            f_debug.write(f"[DOC ERROR] {data_ext}: {href}\n")

    # Add link to frontier
    href_abs = urllib.parse.urljoin(page_url, href)
    href_norm = normalize_url(href_abs)
    frontier_append(cur, href_norm, page_id, robots)


def crawl(thread_id, conn):
    global is_running

    print("===Thread " + str(thread_id) + " started===")

    f_info = open("info.log", "a", encoding="utf-8")
    f_link = open("onclick.log", "a", encoding="utf-8")
    f_debug = open("debug.log", "a", encoding="utf-8")

    # Create Selenium webdriver and set User-Agent
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", USER_AGENT)
    driver = wirewebdriver.Firefox(profile)
    driver.set_page_load_timeout(SELENIUM_TIMEOUT)

    # Create DB connection cursor
    cur = conn.cursor()

    # Main loop
    while is_running:
        # Get next element in frontier
        if not thread_active[thread_id]:
            time.sleep(0.5) # Add small delay while waiting
        with frontier_lock:
            cur.execute("SELECT id, url FROM crawler.page WHERE page_type_code = 'FRONTIER' ORDER BY accessed_time ASC")
            res = cur.fetchone()
            if res != None:
                cur.execute("UPDATE crawler.page SET page_type_code = 'PROCESSING' WHERE id = %s", (res[0],))
            frontier_element = res

            if frontier_element == None:
                thread_active[thread_id] = False
                if not any(thread_active):
                    break
                continue
            thread_active[thread_id] = True

        # Get URL and domain
        page_id, page_url = frontier_element
        # print(f"[{thread_id}] Processing URL: " + page_url)
        domain = urllib.parse.urlparse(page_url).netloc
        
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
                    time.sleep(0.1) # Small delay before getting next frontier element
                    continue
            else:
                crawl_delay = CRAWL_DELAY
                if robots != None:
                    cd = robots.crawl_delay(USER_AGENT)
                    if cd != None:
                        crawl_delay = float(cd)
                history[domain] = (time.time(), crawl_delay)

        # Get HTTP header code
        http_status_code = None
        page_content_type = None
        try:
            response = requests.head(page_url, allow_redirects=True, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
            http_status_code = response.status_code
            if "Content-Type" in response.headers:
                page_content_type = response.headers['Content-Type']
        except requests.exceptions.SSLError:
            pass
        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.ConnectionError:
            pass
        except Exception as e:
            print(f"[HEAD UNKNOWN] Error getting URL HEAD: {page_url}\n\t{e}")
            f_debug.write(f"[HEAD UNKNOWN] Error getting URL HEAD: {page_url}\n\t{e}\n")
        
        if page_content_type != None and not page_content_type.startswith("text/"):
            cur.execute("UPDATE crawler.page " +
                "SET site_id = %s, page_type_code = 'BINARY', " +
                "http_status_code = %s, accessed_time = now() " +
                "WHERE id = %s", (site_id, http_status_code, page_id))
            continue

        
        # Get html
        try:
            driver.get(page_url)
            time.sleep(SELENIUM_WAIT)
        except TimeoutException:
            print(f"[GET TIMEOUT] Timeout on URL: {page_url}\n")
            f_debug.write(f"[GET TIMEOUT] Timeout on URL: {page_url}\n\n")
            with frontier_lock:
                cur.execute("UPDATE crawler.page " +
                "SET site_id = %s, page_type_code = 'UNAVAILABLE', html_content = NULL, " +
                "html_hash = NULL, http_status_code = NULL, accessed_time = now() " +
                "WHERE id = %s", (site_id, page_id))
            continue
        except Exception as e:
            print(f"[GET UNKNOWN] Unable to get URL: {page_url}\n\t{e}")
            f_debug.write(f"[GET UNKNOWN] Unable to get URL: {page_url}\n\t{e}\n")
            with frontier_lock:
                cur.execute("UPDATE crawler.page " +
                "SET site_id = %s, page_type_code = 'UNAVAILABLE', html_content = NULL, " +
                "html_hash = NULL, http_status_code = NULL, accessed_time = now() " +
                "WHERE id = %s", (site_id, page_id))
            continue
        html = driver.page_source
        driver_requests = {}
        for request in driver.requests:
            driver_requests[request.url] = request.response

        # Get html hash and check for duplicates
        html_hash = str(hash(html))
        cur.execute("SELECT id FROM crawler.page WHERE html_hash = %s", (html_hash,))
        res = cur.fetchone()
        if res != None: # Duplicate detected
            duplicate_page_id = res[0]
            cur.execute("UPDATE crawler.page " +
                "SET site_id = %s, page_type_code = 'DUPLICATE', html_content = NULL, " +
                "html_hash = NULL, http_status_code = %s, accessed_time = now() " +
                "WHERE id = %s", (site_id, http_status_code, page_id))
            cur.execute("INSERT INTO crawler.link(from_page, to_page) VALUES (%s, %s)", (page_id, duplicate_page_id))
            continue

        # Update page in DB
        cur.execute("UPDATE crawler.page " +
            "SET site_id = %s, page_type_code = 'HTML', html_content = %s, " +
            "html_hash = %s, http_status_code = %s, accessed_time = now() " +
            "WHERE id = %s", (site_id, html, html_hash, http_status_code, page_id))
            
        # Find all href links
        elems = driver.find_elements_by_xpath("//a[@href]") # "//body//*[@href]"
        for elem in elems:
            href = elem.get_attribute("href")
            if href != None:
                process_link(cur, page_id, page_url, robots, href, f_info, f_link, f_debug)
        # Check if any non-<a> tags contain href for debugging purposes
        elems = driver.find_elements_by_xpath("//body//*[@href]")
        for elem in elems:
            href = elem.get_attribute("href")
            if elem.tag_name != "a" and href != None and not href.startswith("#"):
                f_debug.write(f"[HREF TAG] <{elem.tag_name}>, href='{href}' on URL {page_url}\n")

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
                        f_link.write(onclick_url + "\n")
                        process_link(cur, page_id, page_url, robots, onclick_url, f_info, f_link, f_debug)

                f_link.write("\n\n")

        # Find all images
        elems = driver.find_elements_by_xpath("//img[@src]")
        for elem in elems:
            img_src = elem.get_attribute("src")
            if img_src != None:
                # Ignore base64 images
                if (img_src.startswith("data:")):
                    continue

                # Get image name
                img_path = urllib.parse.urlparse(img_src).path
                # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/img
                img_exts = [".jpg", ".jpeg", ".png", 
                    ".svg", ".gif", ".webp", ".apng", ".avif",
                    ".bmp", ".ico", ".cur", ".tif", ".tiff"]
                img_name = None
                img_ext = None
                for img_ext in img_exts:
                    if img_path.lower().endswith(img_ext):
                        img_name = os.path.basename(img_path)
                        break
                if img_name == None:
                    img_name = os.path.basename(img_path)
                    if img_name == "":
                        print(f"[IMG NAME ERROR] {img_src}")
                        f_debug.write(f"[IMG NAME ERROR] {img_src}\n")
                        img_name = None

                # Get image content type
                img_url = urllib.parse.urljoin(page_url, img_src)
                img_content_type = None
                if img_url in driver_requests: # img_src
                    # Check Selenium request
                    response = driver_requests[img_url]
                    if response and response.status_code == 200 and "Content-Type" in response.headers:
                        img_content_type = response.headers["Content-Type"]
                else:
                    # Manually send request
                    try:
                        response = requests.head(img_url, allow_redirects=True, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
                        if response.status_code == 200 and "Content-Type" in response.headers:
                            img_content_type = response.headers["Content-Type"]
                    except requests.exceptions.SSLError:
                        f_debug.write(f"[IMG HEAD SSL] SSL exception on src: {img_url}\n")
                    except requests.exceptions.Timeout:
                        f_debug.write(f"[IMG HEAD TIMEOUT] Timeout exception on src: {img_url}\n")
                    except requests.exceptions.ConnectionError:
                        f_debug.write(f"[IMG HEAD CONNECTION] Connection error on src: {img_url}\n")
                        pass
                    except Exception as e:
                        print(f"[IMG HEAD UNKNOWN] Unknown exception on src: {img_url}\n\tOn page: {page_url}\n\t{e}")
                        f_debug.write(f"[IMG HEAD UNKNOWN] Unknown exception on src: {img_url}\n\t{e}\n")
                # If requests failed, get content type from filename
                if img_content_type == None and img_ext != None:
                    img_content_type = f"image/{img_ext[1:]}"
                

                if img_name == None or img_content_type == None:
                    print(f"[IMG META ERROR] {img_src}")
                    f_debug.write(f"[IMG META ERROR] {img_src}\n")


                cur.execute("INSERT INTO crawler.image(page_id, filename, content_type) " +
                    "VALUES (%s, %s, %s) ", (page_id, img_name, img_ext))

                # if img_name == None:
                #     print(f"[IMG UNSUPP] {img_src}")
                #     f_debug.write(f"[IMG UNSUPP] {img_src}\n")

                # else:
                #     print(f"[IMAGE] {img_ext} : {img_name}")

    # Cleanup
    f_info.close()
    f_link.close()
    f_debug.close()

    thread_active[thread_id] = False
    cur.close()
    driver.close()
    print("===Thread " + str(thread_id) + " finished===")


# Accept socket connections and process messages
def listen(sock):
    global is_running
    while is_running:
        conn, _ = sock.accept()
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                elif data == b"kill":
                    print("[SERVER] Received kill signal, stopping ...")
                    is_running = False
                    break


if __name__ == "__main__":
    # Create server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # IPv4, TCP
    sock.bind(("localhost", 2803)) # localhost:2803
    sock.listen()

    # Connect to DB
    conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
    conn.autocommit = True

    # Add seed URLs to frontier
    if len(SEED_URLS) > 0:
        with conn.cursor() as cur:
            for seed_url in SEED_URLS:
                frontier_append(cur, seed_url, None, None)

    # Start the crawler
    # crawl(0, conn)
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS+1) as executor:
        # Start server thread
        future_listen = executor.submit(listen, sock)
        # Start crawler threads
        futures = []
        for i in range(NUM_THREADS):
            futures.append(executor.submit(crawl, i, conn))
        # Join crawler threads
        for future in futures:
            future.result()
        is_running = False
        # Stop server thread
        sock.close()
        
   
    # Cleanup
    conn.close()

