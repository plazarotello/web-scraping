from misc import config

from .fotocasa import FotocasaScraper
from .idealista import IdealistaScraper
from .kasaz import KasazScraper
from .pisoscom import PisosComScraper
from .scraper_base import HouseScraper


class ScraperFactory():

    @staticmethod
    def create_scraper(id : str) -> HouseScraper:
        if id == config.FOTOCASA_ID: return FotocasaScraper(id)
        if id == config.IDEALISTA_ID: return IdealistaScraper(id)
        elif id == config.PISOSCOM_ID: return PisosComScraper(id)
        elif id == config.KASAZ_ID: return KasazScraper(id)
        else: raise TypeError(f'No scraper found for the id [{id}]')
