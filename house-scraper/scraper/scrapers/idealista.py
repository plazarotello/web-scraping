from .scraper_base import HouseScraper
from time import sleep
from misc import utils
from concurrent.futures import ThreadPoolExecutor
import re
from selenium.common.exceptions import NoSuchElementException

class IdealistaScraper(HouseScraper):
    BASE_URL = 'https://www.idealista.com'

    def _scrape_location(self, location : str, url : str):
        """
        Scrapes a location in idealista and puts all the info in the TMP folder
        of the project, under idealista/location.txt

        Parameters
        ----------
        location : str
            Name of the location to scrape
        url : str
            URL to be attached to the BASE_URL in order to scrape
        """
        _file = HouseScraper._create_tmp_file(self.id, file_name=location+'.txt')
        with utils.get_selenium() as driver:
            driver.get(self.BASE_URL+url)
            while True:
                main_content = driver.find_element_by_css_selector('main#main-content > section.items-container')
                articles = main_content.find_elements_by_css_selector('article.item')
                for article in articles:
                    # browse all articles
                    sleep(0.5)
                    article.find_element_by_css_selector('div.item-info-container > a.item-link').click()
                    sleep(1.0)
                    
                    house = dict()
                    house['url'] = driver.current_url
                    article_section = driver.find_element_by_css_selector('div#wrapper > div#main naub')
                    # more info TODO
                    driver.back()
                try:
                    next_page = main_content.find_element_by_css_selector('div.pagination > ul > li.next > a')
                    next_page.click()
                except NoSuchElementException as e:
                    print(f'[{self.id}] {e}')
                    break   # no more pages to navigate to
            


    def scrape(self):
        HouseScraper._create_tmp_dir(self.id)

        try:
            soup = HouseScraper._get_url(url=self.BASE_URL)
            section = soup.find_all('section', id='municipality-search')[0]
            # gets all top level locations
            locations_list = section.find_all('div', {'class': 'locations-list'})[0].ul.find_all('li', recursive=False)
            
            # gets a pair of (province, url) for each location
            locations_urls = dict()
            for location in locations_list:
                loc = location.a
                # bypass choosing a sublocation
                locations_urls[loc.string] = re.sub(r'municipios$', '', loc['href'])
        except Exception as e: 
            print(f'[{self.id}]: {e}')
        
        # concurrent scrape of all provinces, using 5 threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            for location, url in locations_urls.items():
                executor.submit(self._scrape_location, location, url)