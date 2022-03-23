from scrapers.scraper_base import HouseScraper
from scrapers.kasaz import KasazScraper
from scrapers.idealista import IdealistaScraper
from scrapers.fotocasa import FotocasaScraper
from scrapers.pisoscom import PisosComScraper

class ScraperFactory():

    @staticmethod
    def create_scraper(id : str) -> HouseScraper:
        if id == 'fotocasa': return FotocasaScraper(id)
        if id == 'idealista': return IdealistaScraper(id)
        elif id == 'pisos.com': return PisosComScraper(id)
        elif id == 'kasaz': return KasazScraper(id)
        else: raise TypeError(f'No scraper found for the id [{id}]')