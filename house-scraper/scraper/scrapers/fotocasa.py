from .scraper_base import HouseScraper
import csv
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from misc import config, utils
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

class FotocasaScraper(HouseScraper):

    __urls = dict()

    def _scrape_house_page(self, location: str, url : str) -> dict: 
        """
        Scrapes a certain house detail page

        Parameters
        ----------
        location: str
            Location the house in in
        url : str
            URL to scrap
        
        Returns
        -------
        Dictionary with all the info on the house
        """
        with utils.get_selenium() as driver:
            try:
                house = {'id': '', 'url': '', 'title': '', 'location': '', 'sublocation': '',
                    'price': '', 'm2': '', 'rooms': '', 'floor': '', 'photos': '', 'map': '',
                    'view3d': '', 'video': '', 'home-staging': '', 'description': ''}
                utils.log(f'[fotocasa:{location}] Scraping {url}')
                utils.mini_wait()
                driver.get(url)
                main_content = self.try_page(driver, lambda: driver.find_element(by=By.CSS_SELECTOR, value='#App > div.re-Page > main > div.re-LayoutContainer.re-LayoutContainer--large > div.re-ContentDetail-topContainer'))
                house['id'] = re.findall('\d+', url)[0]
                house['url'] = driver.current_url
                house['title'] = main_content.find_element(by=By.CSS_SELECTOR, value='div > section:nth-child(1) > div > div.re-DetailHeader-header > div.re-DetailHeader-propertyTitleContainer > h1').text
                house['location'] = location
                house['sublocation'] = "sublocation"
                house['price'] = main_content.find_element(by= By.CSS_SELECTOR, value='div > section:nth-child(1) > div > div.re-DetailHeader-header > div.re-DetailHeader-userActionContainer > div.re-DetailHeader-priceContainer > span').text.replace(' €', '')
                house['description'] = main_content.find_element(by=By.CSS_SELECTOR, value='div > section:nth-child(1) > div > div.fc-DetailDescriptionContainer > div.sui-MoleculeCollapsible.sui-MoleculeCollapsible--withGradient.is-collapsed > div > div > p').text.strip()
                
                house['m2'] =  main_content.find_element(by=By.CSS_SELECTOR, value='div > section:nth-child(1) > div > div.re-DetailHeader-header > div.re-DetailHeader-propertyTitleContainer > ul > li:nth-child(3) > span:nth-child(2) > span').text
                house['rooms'] = main_content.find_element(by=By.CSS_SELECTOR, value='div > section:nth-child(1) > div > div.re-DetailHeader-header > div.re-DetailHeader-propertyTitleContainer > ul > li:nth-child(1) > span:nth-child(2) > span').text
                house['floor'] = main_content.find_element(by=By.CSS_SELECTOR, value='div > section:nth-child(1) > div > div.re-DetailHeader-header > div.re-DetailHeader-propertyTitleContainer > ul > li:nth-child(4) > span:nth-child(2) > span').text
                house['baths'] = main_content.find_element(by=By.CSS_SELECTOR, value='div > section:nth-child(1) > div > div.re-DetailHeader-header > div.re-DetailHeader-propertyTitleContainer > ul > li:nth-child(2) > span:nth-child(2) > span').text
                
                house['num_photos'] = driver.find_element(by=By.CSS_SELECTOR, value='#App > div.re-Page > main > ul > li > button > span > span.sui-AtomButton-text').text.replace(" Fotos","")
                house['map'] = 0
                house['video'] = 0
                house['home-staging'] = 0

                try:
                    driver.find_element(by=By.CSS_SELECTOR, value='#App > div.re-Page > main > ul > li:nth-child(2) > button')
                    house['view3d'] = 1
                except NoSuchElementException:
                    house['view3d'] = 0

                '''
                TODO gestionar urls de las imagenes y su descarga
                resultSet = driver.find_element(by=By.CSS_SELECTOR, value='#re-DetailMultimediaModal > div > div > div.sui-MoleculeModalContent.sui-MoleculeModalContent--without-indentation > div > div.re-DetailMultimediaModal-listColumn > ul.re-DetailMultimediaModal-listWrapper')
                image_list = resultSet.find_elements_by_tag_name("li")
                print("......",image_list)
                for image in image_list:
                    print("--------",image.text)
                '''
                utils.mini_wait()
                return house
            except NoSuchElementException as e:
                utils.error(f'[{self.id}] Something happened!')
                utils.error(f'Exception: {e.msg}')
                return None
    

    def _scrape_houses_details(self,location, houses_list) -> list:
        houses = list()
        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            futures = []
            max_houses_before_wait = 5
            house_number = 0
            #for url, location in self.__urls.items():
            for house_url in houses_list:
                futures.append(executor.submit(self._scrape_house_page, location, house_url))
                house_number = house_number+1
                if house_number >= max_houses_before_wait:
                    house_number = 0
                    utils.mega_wait()
            for future in as_completed(futures):
                house = future.result()
                houses.append(house)    # can append None values
        return list(filter(None, houses))

    def try_page(self, driver, fn):
        madeit = False
        while not madeit:   
            try:
                result = fn()
                madeit = True
            except NoSuchElementException:
                utils.error(NoSuchElementException)
                madeit=False
        return result

    def _scrape_navigation(self, url : str, location : str) -> list:
        """
        Scrapes the navigation pages for a location (given in the starting url).

        Parameters
        ----------
        url : str
            URL to start the scraping
        
        Returns
        -------
        List of the relative URL of the houses that are present in the navigation pages
        """
        driver = utils.get_selenium()
        utils.mini_wait()
        driver.get(url)
        houses_to_visit = list()
        max_pages_before_wait = 5
        page_number = 0

        while True:
            # see how much we have to wait
            utils.mini_wait() if utils.flip_coin() else utils.wait()
            # browse all pages
            main_content = self.try_page(driver, lambda : driver.find_element(by=By.CSS_SELECTOR, 
                    value='#App > div.re-Page > div.re-SearchPage > main > div > div.re-SearchResult-wrapper > section'))

            articles = main_content.find_elements(by=By.CSS_SELECTOR, value='article')
            print(f"numero de articulos {len(articles)}")
            for article in articles:
                # get each article url
                try:
                    house_urls = article.find_element(by=By.CSS_SELECTOR, 
                        value='a.re-CardPackPremium-carousel').get_attribute('href')
                    print(f"found article url: {house_urls}")
                    houses_to_visit.append(house_urls)
                    self.__urls.update(dict.fromkeys(house_urls, location))
                except Exception as e:
                    utils.error(e)
                #
            try:
                next_page = main_content.find_element(by=By.CSS_SELECTOR, value='App > div.re-Page > div.re-SearchPage > main > div > div.re-Pagination > ul > li:nth-child(7) > a')
                driver.execute_script('arguments[0].scrollIntoView();', next_page)
                utils.mini_wait()
                
                page_number = page_number+1
                if page_number >= max_pages_before_wait:
                    page_number = 0
                    utils.mega_wait()
                
                next_page.click()
            except NoSuchElementException as e:
                utils.log(f'[{self.id}] No more pages to visit')
                utils.warn(f'[{self.id}] {e.msg}')
                break   # no more pages to navigate to
        
        utils.mini_wait()
        driver.quit()
        print(f"houses_to_visit: {houses_to_visit}")
        return houses_to_visit

    def scrape(self):
            """
            Scrapes the entire idealista website
            """

            # create url using municiplity name only. Not necessary to invoke main page to get url-muniipality pair 
            location = "fuenlabrada"
            url_call = f"{config.FOTOCASA_URL}comprar/viviendas/{location}/todas-las-zonas/l?sortType=scoring"
            houses_list = self._scrape_navigation(url_call, location)

            houses = self._scrape_houses_details(location, houses_list)

            # mix all the data, keep unique IDs
            utils.log('Merging the data')
            house_fields = ['id', 'url', 'title', 'location', 'sublocation',
                'price', 'm2', 'rooms', 'floor', 'photos', 'map', 'view3d', 
                'video', 'home-staging', 'description']
            #df = pd.DataFrame(houses, columns=house_fields).drop_duplicates('id')

            if not utils.directory_exists(config.DATASET_DIR):
                utils.create_directory(config.DATASET_DIR)
            utils.log(f'Dumping dataset into {config.FOTOCASA_FILE}')
            #df.to_csv(config.FOTOCASA_FILE)
            utils.log(f'Dumped dataset into {config.FOTOCASA_FILE}')

