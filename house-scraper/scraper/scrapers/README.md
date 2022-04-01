Module with the scrapers that crawl each real estate pages. Contains:

- `scraper_factory.py`: factory that creates the most suitable scraper for each case.
- `scraper_base.py`: parent of each scraper implementation. Contains properties and functions used by all scrapers, and the interface each has to implement.
- `idealista.py`: scraps idealista.com.
- `fotocasa.py`: scraps fotocasa.es.
- `pisoscom.py`: scraps pisos.com.
- `kasaz.py`: scraps kasaz.com
