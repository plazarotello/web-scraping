Main module of the web scrapper. Contains:

- `__main__.py`: main program. Will scrap several second hand real state seller pages and collect the results in a single file.
- `chrome_setup.py`: program to create the chrome session. Needs user interaction to bypass the CAPTCHAs.
- `scrapers`: submodule with the scrapers that handle each seller page.
- `misc`: submodule with utilities and other miscellanous functions.
