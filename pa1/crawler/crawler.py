from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from url_normalize import url_normalize
import psycopg2
import urllib
import urllib.request
import urllib.robotparser
import requests
import hashlib

USER_AGENT = "fri-ieps-mr"


def curl(url):
    try:
        res = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=5)
        if res.status_code == 200:
            return res.text
    except:
        return None
    return None


frontier = [
    "http://gov.si",
    # "http://evem.gov.si",
    # "http://e-uprava.gov.si",
    # "http://e-prostor.gov.si"
]


driver = webdriver.Firefox()

# Connect to DB
conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
conn.autocommit = True

while len(frontier) > 0:
    # Get URL and domain
    url = frontier.pop(0)
    # TODO Get canonical URL
    # url = ...
    domain = urllib.parse.urlparse(url).netloc

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
        
        robots = urllib.robotparser.RobotFileParser()
        if robots_content != None:
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
    print(http_status_code)

    # Insert page into DB
    cur.execute("INSERT INTO crawler.page(site_id, url, html_content, html_hash, http_status_code, accessed_time)" +
        "VALUES (%s, %s, %s, %s, %s, now()) RETURNING id", (site_id, url, html, html_hash, http_status_code))
    page_id = cur.fetchone()[0]
    print(page_id)

    # Find all links
    elems = driver.find_elements_by_xpath("//a[@href]")
    for elem in elems:
        href = elem.get_attribute("href")
        if href != None:
            href_norm = url_normalize(href)


    cur.close()



conn.close()


driver.close()



# conn = psycopg2.connect(host="localhost", user="user", password="SecretPassword")
# conn.autocommit = True
# cur = conn.cursor()
# cur.execute("INSERT INTO crawler.site(domain) VALUES ('test.com')")
# cur.execute("SELECT domain FROM crawler.site WHERE id = 1")
# value = cur.fetchone()[0]
# cur.close()
# conn.close()

