class HouseScraper():
    """
    Class used to represent a scraper that will crawl through a single 
    real estate listing web

    ...

    Attributes
    ----------
    id : str
        identifier for the scraper

    Methods
    -------
    scrape(urls : str, opt)
        Crawls through a web or a subset of pages in the web

    """

    def __init__(self, id: str):
        self.id = id

    def scrape(self, urls: list = None): raise NotImplementedError
