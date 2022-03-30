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

    def _scrape_houses_details(self,location, houses_list) -> list:
        houses = list()
        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            futures = []
            max_houses_before_wait = 5
            house_number = 0
            #for url, location in self.__urls.items():
            for house_url in houses_list:
                print(house_url)
                #futures.append(executor.submit(self._scrape_house_page, location, house_url))
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
            print("______________________")
            # browse all pages
            main_content = self.try_page(driver, lambda : driver.find_element(by=By.CSS_SELECTOR, 
                    value='#App > div.re-Page > div.re-SearchPage > main > div > div.re-SearchResult-wrapper > section'))

            articles = main_content.find_elements(by=By.CSS_SELECTOR, value='article')
            print(f"numero de articulos {len(articles)}")
            for article in articles:
                # get each article url
                house_urls = article.find_element(by=By.CSS_SELECTOR, 
                    value='a.re-CardPackPremium-carousel').get_attribute('href')
                print(f"found article url: {house_urls}")
                houses_to_visit.append(house_urls)
                self.__urls.update(dict.fromkeys(house_urls, location))

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
            print(houses_list)

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

