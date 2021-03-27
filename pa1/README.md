# Programming Assignment 1

## Setup

* Install Python >= 3.8 and the following packages:
```bash
pip install selenium
pip install selenium-wire
pip install url-normalize
pip install psycopg2
pip install reppy
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

## Database Queries

```
docker exec -it postgresql-wier psql -U user
```
```
SELECT email FROM crawler.email;
SELECT tel FROM crawler.tel;
```


## Questions

* Selenium doesn't detect images (and links?) in `<noscript>`, is this ok?

* How do we find non-image data on a page?
	* Just check if the site is html or not
* How do we get the HTTP status code? Should we send a HEAD request first? What about redirects?
	* Send HEAD first
* If page doesn't exist, should we remove it from the DB?
	* Mark it as not accessible
* For pages, is checking Content-Type header good enough?
	* Yes
* What's a good way to implement crawl delay? Can robots.txt override the 5s rule?
	* Locally, not in DB
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

* Robots http/https test
* Check if link is an image/document
* (DONE) Get images
* (DONE) Remove # from URLs?
* (DONE) Don't send too many requests to the same server too quickly (maybe add a minimum delay) (5 seconds)
* (DONE) Multiple threads
* Collect emails and telephone numbers (for educational purposes only!)
* (DONE) Add link even if site is already in the DB
* (DONE) Selenium timeout when site doesn't load???
* (DONE) Crawl-delay
* (DONE) Add link to existing URLs
* (DONE) Get links from onclick events
* Add DB to repository
* Interrupt handler

## Bugs

* (FIXED) Thread finishing too early
* (FIXED) Multithreaded DB access causing duplicate keys
```
2021-03-16 23:30:21.133 UTC [648] ERROR:  duplicate key value violates unique constraint "uidx_page_url"
2021-03-16 23:30:21.133 UTC [648] DETAIL:  Key (url)=(https://www.e-prostor.gov.si/kontakt/) already exists.
```

## Notes

* Odstranimo # razen ce najdemo protiprimer
* Pri slikah je dovolj da upostevamo ime ali pa content-type header
* Pri onclick preveri VSAJ location.href in document.location
* Filename atribut v headerju za linke ki npr. nimajo koncnice .pdf, ampak je content-type pdf
* ~50k strani


## Technical details

### Document detection

https://www.fu.gov.si/datoteka.php?src=fileadmin/Internet/Drugo/Posebna_podrocja/Turisticni_boni/HU_Priloga_3.docx

### Image detection

Count the images in `<noscript>`? https://podatki.gov.si/

### Other
```
[1] Error visiting URL http://eugo.gov.si/en/sectors-by-catergory/
[5] Error visiting URL https://spot.gov.si/resources/themes/gov/fonts/Republika/ver1.2/republika-bold-webfont.woff2?v=3
[6] Error visiting URL https://spot.gov.si/resources/themes/gov/fonts/Republika/ver1.2/republika-regular-webfont.woff2?v=3
[1] Error visiting URL https://spot.gov.si/sl/portal-in-tocke-spot/o-portalu-spot/
[5] Error visiting URL https://www.stopbirokraciji.gov.si/dobre-prakse
[4] Error visiting URL https://www.gov.si/de/
[IMG HEAD ERR] https://urednik-gov.sigov.si/resources/themes/gov/images/RS_gov_si-logo.gif
        https://urednik-gov.sigov.si/resources/themes/gov/images/RS_gov_si-logo.gif
[1] Error visiting URL https://eugo.gov.si/
[2] Error visiting URL https://prostor4.gov.si/imps/srv/slv/catalog.search
```
