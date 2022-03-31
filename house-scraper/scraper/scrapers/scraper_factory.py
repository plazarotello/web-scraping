from misc import config

from .fotocasa import FotocasaScraper
from .idealista import IdealistaScraper
from .scraper_base import HouseScraper


class ScraperFactory():

    @staticmethod
    def create_scraper(id : str) -> HouseScraper:
        if id == config.FOTOCASA_ID: return FotocasaScraper(id)
        if id == config.IDEALISTA_ID: return IdealistaScraper(id)
        else: raise TypeError(f'No scraper found for the id [{id}]')