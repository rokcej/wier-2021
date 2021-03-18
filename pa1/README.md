# Programming Assignment 1

## Setup

* Install Python >= 3.8 and the following packages:
```bash
pip install selenium
pip install url-normalize
pip install psycopg2
```
* Download geckodriver (Firefox WebDriver) and add it to `PATH`
```bash
sudo apt-get install firefox-geckodriver
```
* Install docker and create a PostgreSQL container:
```bash
docker run --name postgresql-wier -e POSTGRES_PASSWORD=SecretPassword \
-e POSTGRES_USER=user -v $PWD/db/pgdata:/var/lib/postgresql/data \
-v $PWD/db/init-scripts:/docker-entrypoint-initdb.d -p 5432:5432 -d postgres:12.2
```
* Run the crawler:
```bash
python crawler/crawler.py
```


## Questions

* How do we find non-image data on a page?
* How do we get the HTTP status code?
* If page doesn't exist, should we remove it from the DB?

* If page doesn't exist, should the site be stored in the DB?
	* Yes
* How to know if response is text or not? (e.g. sitemap) application/xml
	* Current approach good enough
* What's a good way to view / manage the DB?
	* Pgadmin
* Should we store the frontier in the DB? (if we stop the crawler while the frontier isn't empty)
	* Yes
* Should the 5 second limit apply to the domain or IP? (how do we get the IP?)
	* Domain is good enough
* Can we remove # at the end
	* Yes, unless you find an example where it wouldn't be safe

## TODO

* Get images
* Remove # from URLs?
* Don't send too many requests to the same server too quickly (maybe add a minimum delay) (5 seconds)
* Multiple threads
* Collect emails and telephone numbers (for educational purposes only!)
* Add link even if site is already in the DB
* Selenium timeout when site doesn't load???
* Crawl-delay
* Add link to existing URLs
* Get links from onclick events
* Add DB to repository

## Bugs

* (FIXED) Thread finishing too early
* (FIXED) Multithreaded DB access causing duplicate keys
```
2021-03-16 23:30:21.133 UTC [648] ERROR:  duplicate key value violates unique constraint "uidx_page_url"
2021-03-16 23:30:21.133 UTC [648] DETAIL:  Key (url)=(https://www.e-prostor.gov.si/kontakt/) already exists.
```

## Notes

* Odstranimo # razen ce najdemo protiprimer

