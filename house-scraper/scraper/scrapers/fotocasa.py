from .scraper_base import HouseScraper
import csv
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import pandas as pd
from misc import config, utils
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class FotocasaScraper(HouseScraper):

    __urls = dict()

    def _scrape_house_page(self, location: str, url : str) -> dict: 
        """
        Scrapes a certain house detail page

        Parameters
        ----------
        location: str
            Location the house is in
        url : str
            URL to scrap
        
        Returns
        -------
        Dictionary with all the info on the house
        """
        with utils.get_selenium() as driver:
            try:
                house = {'id': '', 'url': '', 'title': '', 'location': '', 
                    'price': '', 'm2': '', 'rooms': '', 'floor': '', 'num-photos': '','floor-plan': '','view3d': '',
                    'video': '', 'home-staging': '', 'description': '', 'photo_urls': ''}
                utils.log(f'[fotocasa:{location}] Scraping {url}')
                utils.mini_wait()
                driver.get(url)

                id = re.findall('\d+', url)[0]
                
                # checking if download directory exists
                download_dir = f"{config.FOTOCASA_IMG_DIR}-{location}-imgs/{id}"
                if utils.directory_exists(download_dir) == False:
                    utils.create_directory(download_dir)

                for scroll_i in range(config.FOTOCASA_SCROLL_HOUSE_PAGE):
                    
                    photo_list = []
                    num_img = 1
                    resultSet = driver.find_element(by=By.CSS_SELECTOR, value='#App > div.re-Page > main > section')
                    image_list = resultSet.find_elements_by_tag_name("figure")
                    for image in image_list:
                        img_src = image.find_element(by=By.CSS_SELECTOR, value='img').get_attribute('src')
                        photo_list.append(img_src)
                        utils.download_image(img_src, f"{download_dir}/{num_img}.jpg")
                        num_img = num_img +1
                        


                    main_content = self.try_page(driver, lambda: driver.find_element(by=By.CSS_SELECTOR, value='#App > div.re-Page > main > div.re-LayoutContainer.re-LayoutContainer--large > div.re-ContentDetail-topContainer'))
                    house['id'] = id
                    house['url'] = driver.current_url
                    house['title'] = main_content.find_element(by=By.CSS_SELECTOR, value='div > section:nth-child(1) > div > div.re-DetailHeader-header > div.re-DetailHeader-propertyTitleContainer > h1').text
                    house['location'] = location
                    house['price'] = main_content.find_element(by= By.CSS_SELECTOR, value='div > section:nth-child(1) > div > div.re-DetailHeader-header > div.re-DetailHeader-userActionContainer > div.re-DetailHeader-priceContainer > span').text.replace(' €', '')
                    house['description'] = main_content.find_element(by=By.CSS_SELECTOR, value='div > section:nth-child(1) > div > div.fc-DetailDescriptionContainer > div.sui-MoleculeCollapsible.sui-MoleculeCollapsible--withGradient.is-collapsed > div > div > p').text.strip()
                                                                                        
                    house['m2'] =  main_content.find_element(by=By.CSS_SELECTOR, value='div > section:nth-child(1) > div > div.re-DetailHeader-header > div.re-DetailHeader-propertyTitleContainer > ul > li:nth-child(3) > span:nth-child(2) > span').text
                    house['rooms'] = main_content.find_element(by=By.CSS_SELECTOR, value='div > section:nth-child(1) > div > div.re-DetailHeader-header > div.re-DetailHeader-propertyTitleContainer > ul > li:nth-child(1) > span:nth-child(2) > span').text
                    house['floor'] = main_content.find_element(by=By.CSS_SELECTOR, value='div > section:nth-child(1) > div > div.re-DetailHeader-header > div.re-DetailHeader-propertyTitleContainer > ul > li:nth-child(4) > span:nth-child(2) > span').text
                    house['baths'] = main_content.find_element(by=By.CSS_SELECTOR, value='div > section:nth-child(1) > div > div.re-DetailHeader-header > div.re-DetailHeader-propertyTitleContainer > ul > li:nth-child(2) > span:nth-child(2) > span').text
                    
                    house['num-photos'] = driver.find_element(by=By.CSS_SELECTOR, value='#App > div.re-Page > main > ul > li > button > span > span.sui-AtomButton-text').text.replace(" Fotos","")
                    house['floor-plan'] = 0
                    house['video'] = 0
                    house['home-staging'] = 0

                    try:
                        driver.find_element(by=By.CSS_SELECTOR, value='#App > div.re-Page > main > ul > li:nth-child(2) > button')
                        house['view3d'] = 1
                    except NoSuchElementException:
                        house['view3d'] = 0
                    
                    house['photo_urls'] = photo_list

                    ActionChains(driver).key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
                    time.sleep(0.5)

                utils.mini_wait()
                return house
            
            except NoSuchElementException as e:
                utils.error(f'[{self.id}] Something happened!')
                utils.error(f'Exception: {e.msg}')
                return None

    def _scrape_houses_details(self,location, houses_list) -> list:
        """

        """
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
        '''TODO gestionar cookies en cada página'''
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
        
        location : str
            literal name of the location to scrape
        
        Returns
        -------
            List of the relative URL of the houses that are present in the navigation pages to scrape one by one
        """

        # checking if download directory exists
        download_dir = f"{config.FOTOCASA_IMG_DIR}-{location}-imgs"
        if utils.directory_exists(download_dir) == False:
            utils.create_directory(download_dir)

        driver = utils.get_selenium()
        driver.get(url)

        # accept terms and conditios
        acc = driver.find_element(by=By.CSS_SELECTOR,value='#App > div.re-SharedCmp > div > div > div > footer > div > button.sui-AtomButton.sui-AtomButton--primary.sui-AtomButton--solid.sui-AtomButton--center')
        utils.mini_wait()
        acc.click()

        houses_to_visit = []
        max_pages_before_wait = 5
        page_number = 0
    
        # next page, looking for '>' icon
        last_page = False
        num_page = 0
        while last_page == False:
            num_page = num_page + 1
            utils.log(f"fotocasa - current page {num_page}")
          

            if location == 'villaverde':
                # scroll down and read each house
                for scroll_i in range(config.FOTOCASA_SCROLL_LOCATION_PAGE):
                    ActionChains(driver).key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
                    utils.scroll_wait()

                    # read the page to get huose's urls
                    if num_page == 1:
                        main_content = driver.find_element(by=By.CSS_SELECTOR,value='#App > div.re-Page > div.re-SearchPage > main > div > div.re-SearchResult-wrapper > section')
                        
                        try:
                            articles = main_content.find_elements(by=By.CSS_SELECTOR, value='article.re-CardPackPremium')
                        except Exception as e:
                            articles = main_content.find_elements(by=By.CSS_SELECTOR, value='article.re-CardPackAdvance')
                        
                        for article in articles:
                            # get each article url
                            try:
                                house_urls = article.find_element(by=By.CSS_SELECTOR, value='a.re-CardPackPremium-carousel').get_attribute('href')
                                houses_to_visit.append(house_urls)
                                self.__urls.update(dict.fromkeys(house_urls, location))
                            except Exception as e:
                                utils.error(e)

                    elif num_page == 2:                                              
                        main_content = driver.find_element(by=By.CSS_SELECTOR,value='#App > div.re-Page > div.re-SearchPage > main > div > div.re-SearchResult-wrapper > section')
                        
                        articles = main_content.find_elements(by=By.CSS_SELECTOR, value='article.re-CardPackAdvance')
                        
                        for article in articles:
                            # get each article url
                            try:
                                house_urls = article.find_element(by=By.CSS_SELECTOR, value='a.re-CardPackAdvance-slider').get_attribute('href')
                                houses_to_visit.append(house_urls)
                                self.__urls.update(dict.fromkeys(house_urls, location))
                            except Exception as e:
                                utils.error(e)

                    else:
                        try:
                            main_content = driver.find_element(by=By.CSS_SELECTOR,value='#App > div.re-Page > div.re-SearchPage.re-SearchPage--withMap > main > div > div.re-SearchResult-wrapper > section')
                            
                            articles = main_content.find_elements(by=By.CSS_SELECTOR, value='article.re-CardPackMinimal')
                            
                            for article in articles:
                                # get each article url
                                try:
                                    house_urls = article.find_element(by=By.CSS_SELECTOR, value='a.re-CardPackMinimal-slider').get_attribute('href')
                                    houses_to_visit.append(house_urls)
                                    self.__urls.update(dict.fromkeys(house_urls, location))
                                except Exception as e:
                                    utils.error(e)  
                        except Exception as e:
                            utils.log(e)
            
            if location == 'barrio-de-salamanca':

                # scroll down and read each house
                for scroll_i in range(config.FOTOCASA_SCROLL_LOCATION_PAGE):
                    ActionChains(driver).key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
                    utils.scroll_wait()

                    # read the page to get huose's urls
                    if num_page == 1 or num_page == 2 or num_page == 3:
                        
                        
                        main_content = driver.find_element(by=By.CSS_SELECTOR,value='#App > div.re-Page > div.re-SearchPage > main > div > div.re-SearchResult-wrapper > section')
                        
                        try:
                            articles = main_content.find_elements(by=By.CSS_SELECTOR, value='article.re-CardPackPremium')
                        except Exception as e:
                            utils.error(e)
                        
                        for article in articles:
                            # get each article url
                            try:
                                house_urls = article.find_element(by=By.CSS_SELECTOR, value='a.re-CardPackPremium-carousel').get_attribute('href')
                                houses_to_visit.append(house_urls)
                                self.__urls.update(dict.fromkeys(house_urls, location))
                            except Exception as e:
                                utils.error(e)

                    elif num_page == 4:
                                                                                                                                
                        main_content = driver.find_element(by=By.CSS_SELECTOR,value='#App > div.re-Page > div.re-SearchPage.re-SearchPage--withMap > main > div > div.re-SearchResult-wrapper > section')
                        
                        try:
                            articles = main_content.find_elements(by=By.CSS_SELECTOR, value='article.re-CardPackAdvance')
                        
                        except Exception as e:
                            utils.error(e)
                        
                        for article in articles:
                            # get each article url
                            try:
                                house_urls = article.find_element(by=By.CSS_SELECTOR, value='a.re-CardPackAdvance-slider').get_attribute('href')
                                houses_to_visit.append(house_urls)
                                self.__urls.update(dict.fromkeys(house_urls, location))
                            except Exception as e:
                                utils.error(e)
    
                    else: 
                                                       
                        main_content = driver.find_element(by=By.CSS_SELECTOR,value='#App > div.re-Page > div.re-SearchPage.re-SearchPage--withMap > main > div > div.re-SearchResult-wrapper > section')
                        
                        try:
                            articles = main_content.find_elements(by=By.CSS_SELECTOR, value='article.re-CardPackMinimal')
                        
                        except Exception as e:
                            utils.error(e)
                        
                        for article in articles:
                            # get each article url
                            try:
                                house_urls = article.find_element(by=By.CSS_SELECTOR, value='a.re-CardPackMinimal-slider').get_attribute('href')
                                houses_to_visit.append(house_urls)
                                self.__urls.update(dict.fromkeys(house_urls, location))
                            except Exception as e:
                                utils.error(e)


                # delete duplicates houses     
                houses_set = set(houses_to_visit)
                houses_to_visit = list(houses_set)



            # when finish, next page
            try:
                utils.mini_wait()
                items = driver.find_elements(by=By.CSS_SELECTOR, value='#App > div.re-Page > div.re-SearchPage.re-SearchPage--withMap > main > div > div.re-Pagination > ul > li.sui-MoleculePagination-item')
                for item in items:
                    url_next = item.find_element(by=By.CSS_SELECTOR, value='a')

                driver.get(url_next.get_attribute('href'))
            except Exception as e:
                utils.log(e)
                last_page = True

            # control the maximun pages to process
            if config.FOTOCASA_NUM_PAGES_TO_READ == num_page:
                last_page = True

        print(f"ultima pagina {num_page}")
        
        utils.mini_wait()
        driver.quit()
        utils.log(f"Num of houses_to_visit: {len(houses_to_visit)}")
        return houses_to_visit


    def scrape(self, urls : list = None):
        """
        Scrapes https://www.fotocasa.es/es/
        """
        utils.log("Starting Fotocasa dataset")

        if utils.directory_exists(config.FOTOCASA_IMG_DIR) == False:
            utils.create_directory(config.FOTOCASA_IMG_DIR)


        # create url using municiplity name only. Not necessary to invoke main page to get url-muniipality pair 
        url_call = urls[0]
        location = url_call.split("/")[-2]

        utils.log("Obtaining list of houses")
        houses_list = self._scrape_navigation(url_call, location)
        utils.log("Scrapping houses")
        houses = self._scrape_houses_details(location, houses_list)

        # mix all the data, keep unique IDs
        utils.log('Merging the data')
        house_fields = ['id', 'url', 'title', 'location', 'price', 
        'm2', 'rooms', 'floor', 'num-photos', 'floor-plan', 'view3d', 'video', 
        'home-staging', 'description','photo_urls']
        utils.debug(f"Writing dataframe")
        df = pd.DataFrame(houses, columns=house_fields).drop_duplicates('id')

        if not utils.directory_exists(config.DATASET_DIR):
            utils.create_directory(config.DATASET_DIR)
        
        utils.log(f'Dumping dataset into {config.FOTOCASA_FILE}')
        df.to_csv(config.FOTOCASA_FILE, mode='a')
        utils.log(f'Dumped dataset into {config.FOTOCASA_FILE}')
