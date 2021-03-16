# wier-2021
Web Information Extraction and Retrieval course project

## Questions

* If page doesn't exist, should the site be stored in the DB?
* How to know if response is text or not? (e.g. sitemap)

## TODO

* Get images
* Remove # from URLs?
* Don't send too many requests to the same server too quickly (maybe add a minimum delay)
* Multiple threads
* Collect emails and telephone numbers (for educational purposes only!)

## Bugs

* Thread finishing too early
* Multithreaded DB access
```
2021-03-16 23:30:21.133 UTC [648] ERROR:  duplicate key value violates unique constraint "uidx_page_url"
2021-03-16 23:30:21.133 UTC [648] DETAIL:  Key (url)=(https://www.e-prostor.gov.si/kontakt/) already exists.
```
