from .scraper_base import HouseScraper
from time import sleep
import threading

class IdealistaScraper(HouseScraper):
    BASE_URL = 'https://www.idealista.com'

    def _scrape_location(self, location : str, url : str):
        _file = HouseScraper._create_tmp_file(self.id, file_name=location)

    def scrape(self):
        HouseScraper._create_tmp_dir(self.id)

        try:
            soup = HouseScraper._get_url(url=self.BASE_URL)
            section = soup.find_all('section', id='municipality-search')[0]
            # gets all top level locations
            locations_list = section.find_all('div', {'class': 'locations-list'})[0].ul.find_all('li', recursive=False)
            
            locations_urls = dict()
            for location in locations_list:
                loc = location.a
                locations_urls[loc.string] = loc['href']

            #print(locations_urls)
        except Exception as e: 
            print(f'[{self.id}]: {e}')
        
        # concurrent scrape of all provinces
        scraper_threads = list()
        for location, url in locations_urls.items():
            scraper_thread = threading.Thread(target=self._scrape_location, args=(location, url))
            scraper_threads.append(scraper_thread)
            scraper_thread.start()
        
        for scraper_thread in scraper_threads:
            scraper_thread.join()