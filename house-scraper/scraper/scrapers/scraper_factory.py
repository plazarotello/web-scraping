from .scraper_base import HouseScraper
from .kasaz import KasazScraper
from .idealista import IdealistaScraper
from .fotocasa import FotocasaScraper
from .pisoscom import PisosComScraper

class ScraperFactory():

    @staticmethod
    def create_scraper(id : str) -> HouseScraper:
        if id == 'fotocasa': return FotocasaScraper(id)
        if id == 'idealista': return IdealistaScraper(id)
        elif id == 'pisos.com': return PisosComScraper(id)
        elif id == 'kasaz': return KasazScraper(id)
        else: raise TypeError(f'No scraper found for the id [{id}]')