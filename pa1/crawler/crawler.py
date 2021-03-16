from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from url_normalize import url_normalize
import psycopg2
import urllib
import urllib.request
import urllib.robotparser
import requests

USER_AGENT = "fri-ieps-mr"


def curl(url):
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    return


frontier = [
    "http://gov.si/admin",
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
    domain = urllib.parse.urlparse(url).netloc

    cur = conn.cursor()
    
    # Get site data
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
            if (len(sitemaps) > 0):
                sitemap_content = curl(sitemaps[0])
            else:
                sitemap_content = curl("http://" + domain + "/sitemap.xml")
        cur.execute("INSERT INTO crawler.site(domain, robots_content, sitemap_content) VALUES (%s, %s, %s)", (domain, robots_content, sitemap_content))
    else:
        # Fetch site from DB
        robots_content = res[2]
        if robots_content != None:
            robots = urllib.robotparser.RobotFileParser()
            robots.parse(robots_content.split('\n'))
        #print(res[0], res[1], res[2], res[3])

    cur.close()

    # Check robots.txt
    if robots != None:
        if not robots.can_fetch(USER_AGENT, url):
            print("Disallowed!")
            continue


    # # Get html
    # driver.get(url)
    # title = driver.title
    # html = driver.page_source

    # # Get html hash
    # # TODO

    # # Find all links
    # elems = driver.find_elements_by_xpath("//a[@href]")
    # for elem in elems:
    #     href = elem.get_attribute("href")
    #     if href != None:
    #         href_norm = url_normalize(href)



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

