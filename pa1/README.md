# Programming Assignment 1

## Parameters

* `USER_AGENT` - The name of the crawler
* `SEED_URLS` - List of URLs that are initially added to the frontier
* `NUM_THREADS` - Number of parallel workers to use
* `CRAWL_DELAY` - Minimum default crawl delay
* `SELENIUM_WAIT` - Minimum waiting time when loading pages with Selenium
* `SELENIUM_TIMEOUT` - Maximum waiting time when loading pages with Selenium
* `REQUEST_TIMEOUT` - Maximum waiting time when manually sending GET and HEAD requests

## Setup

* Install Python >= 3.8 and the following packages:
```bash
pip install selenium
pip install selenium-wire
pip install url-normalize
pip install psycopg2
pip install reppy
```
* Download geckodriver (Firefox WebDriver) and add it to `PATH`:
```bash
sudo apt-get install firefox-geckodriver
```
* Install docker and create a PostgreSQL container:
	* Make sure you init the database with `database/init-scripts/database.sql`
	* Make sure the database can be accessed with: `host="localhost"`, `user="user"`, `password="SecretPassword"`
```bash
docker run --name postgresql-wier -e POSTGRES_PASSWORD=SecretPassword \
-e POSTGRES_USER=user -v $PWD/databaase/pgdata:/var/lib/postgresql/data \
-v $PWD/database/init-scripts:/docker-entrypoint-initdb.d -p 5432:5432 -d postgres:12.2
```
* Run the crawler:
```bash
python crawler/crawler.py
```


## Statistics

### Sites
Total: 290

### Pages
HTML: 26766
Duplicate: 880
Binary: 2694
Unavailable: 501
Disallowed: 10400
Frontier: 90445

Total: 131686

### Links
Between HTML, Binary, Duplicate: 1936828

Total: 2888682

### Files
PDF: 26481
DOC*: 7425
	(doc: 3574)
	(docx: 3849)
	(docm: 2)
PPT*: 161
	(ppt: 59)
	(pptx: 100)
	(pptm: 2)
XLS*: 2332
	(xls: 1020)
	(xlsx: 1212)
	(xlsm: 100)
Compressed: 5895
	(ZIP: 5894)
	(RAR: 5)
CSV: 478

Total: 42776
Avg files per page: 1.60

### Images
JPG: 26940
	(jpg: 583)
	(jpeg: 26188)
	(pjpeg: 169)
PNG: 104241
GIF: 77716
SVG: 95040
BMP: 22
TIFF: 87

Total: 304046
Avg images per page: 11.36


### Other
Telephone numbers: 1794
Emails: 1338


## Database management

* Connecting to the database:
```
docker run -p 80:80 -e 'PGADMIN_DEFAULT_EMAIL=user@domain.com' -e 'PGADMIN_DEFAULT_PASSWORD=SecretPassword' -d dpage/pgadmin4
```
* Useful queries:
```
SELECT pg1.site_id, pg2.site_id
FROM crawler.link AS lnk
	INNER JOIN crawler.page AS pg1 ON lnk.from_page = pg1.id
	INNER JOIN crawler.page AS pg2 ON lnk.to_page = pg2.id;
```
```
SELECT COUNT(*)
FROM crawler.link AS lnk
	INNER JOIN crawler.page AS pg1 ON lnk.from_page = pg1.id
	INNER JOIN crawler.page AS pg2 ON lnk.to_page = pg2.id
WHERE
	(pg1.page_type_code = 'HTML' OR pg1.page_type_code = 'BINARY' OR pg1.page_type_code = 'DUPLICATE') AND
	(pg2.page_type_code = 'HTML' OR pg2.page_type_code = 'BINARY' OR pg2.page_type_code = 'DUPLICATE') ;
```
```
SELECT content_type, count(*) FROM crawler.image GROUP BY content_type;
```
