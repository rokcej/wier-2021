# Programming Assignment 1

## Questions

* How do we find non-image data on a page?
* How do we get the HTTP status code?
* If page doesn't exist, should we remove it from the DB?

* If page doesn't exist, should the site be stored in the DB?
Yes
* How to know if response is text or not? (e.g. sitemap) application/xml
Current approach good enough
* What's a good way to view / manage the DB?
Pgadmin
* Should we store the frontier in the DB? (if we stop the crawler while the frontier isn't empty)
Yes
* Should the 5 second limit apply to the domain or IP? (how do we get the IP?)
Domain is good enough
* Can we remove # at the end
Yes, unless you find an example where it wouldn't be safe

## TODO

* Get images
* Remove # from URLs?
* Don't send too many requests to the same server too quickly (maybe add a minimum delay)
* Multiple threads
* Collect emails and telephone numbers (for educational purposes only!)
* Add link even if site is already in the DB
* Selenium timeout when site doesn't load???

## Bugs

* Thread finishing too early
* Multithreaded DB access
```
2021-03-16 23:30:21.133 UTC [648] ERROR:  duplicate key value violates unique constraint "uidx_page_url"
2021-03-16 23:30:21.133 UTC [648] DETAIL:  Key (url)=(https://www.e-prostor.gov.si/kontakt/) already exists.
```

## Notes

* Odstranimo # razen ce najdemo protiprimer

