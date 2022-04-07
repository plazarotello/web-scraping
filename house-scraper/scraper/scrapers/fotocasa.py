from .scraper_base import HouseScraper
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from misc import config, utils
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

class FotocasaScraper(HouseScraper):

    __urls = dict()

    def _scrape_house_page(self, location: str, url : str) -> dict: 
        """
        Scrapes a certain house detail page

        Parameters
        ----------
        location: str
            Location where the house is in
        url : str
            URL to scrape
        
        Returns
        -------
        Dictionary with all the info from the house
        """

        # gets conexion with Selenium driver
        with utils.get_selenium() as driver:
            try:

                # defines header dictionary for data
                house = {'id': '', 'url': '', 'title': '', 'location': '', 
                    'price': '', 'm2': '', 'rooms': '', 'floor': '', 'num-photos': '','floor-plan': '','view3d': '',
                    'video': '', 'home-staging': '', 'description': '', 'photo_urls': ''}
                utils.log(f'[fotocasa:{location}] Scraping {url}')
                utils.mini_wait()
                driver.get(url)
                id = re.findall('\d+', url)[0]
                
                # checks if download directory exists, crates it otherwise
                download_dir = f"{config.FOTOCASA_IMG_DIR}-{location}-imgs/{id}"
                if utils.directory_exists(download_dir) == False:
                    utils.create_directory(download_dir)
                
                # scrolls down the page
                for scroll_i in range(config.FOTOCASA_SCROLL_HOUSE_PAGE):
                    
                    # read photo data and download them 
                    photo_list = []
                    num_img = 1
                    resultSet = driver.find_element(by=By.CSS_SELECTOR, value='#App > div.re-Page > main > section')
                    image_list = resultSet.find_elements_by_tag_name("figure")
                    for image in image_list:
                        img_src = image.find_element(by=By.CSS_SELECTOR, value='img').get_attribute('src')
                        photo_list.append(img_src)
                        utils.download_image(img_src, f"{download_dir}/{num_img}.jpg")
                        num_img = num_img +1

                    # retrieve data from each house container
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

                    # scrolls down action and waits
                    ActionChains(driver).key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
                    utils.mini_wait()

                utils.mini_wait()
                return house
            
            except NoSuchElementException as e:
                utils.error(f'[{self.id}] Something happened!')
                utils.error(f'Exception: {e.msg}')
                return None

    def _scrape_houses_details(self, location, houses_list) -> list:
        """
        Creates several threads to process each house

        Parameters
        ----------        
        location : str
            literal name of the location to scrape
        
        houses_list : lst
            List of the URL of the houses to scrape
        
        Returns
        -------
            List with the houses data
        """
        houses = list()
        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            futures = []
            max_houses_before_wait = 5
            house_number = 0
            # for url, location in self.__urls.items()
            for house_url in houses_list:

                # creates threads to process each URL house
                futures.append(executor.submit(self._scrape_house_page, location, house_url))
                house_number = house_number + 1
                if house_number >= max_houses_before_wait:
                    house_number = 0
                    utils.mega_wait()
            
            # Once all houses were processed, the list with data is created
            for future in as_completed(futures):
                house = future.result()
                houses.append(house)

        return list(filter(None, houses))

    def try_page(self, driver, fn):
        """
        Tries to access the element provided in fn (find_element() usually)

        Parameters
        ----------
        driver
            Selenium driver
        fn : function
            Function to execute on the driver

        Returns
        -------
        The result of executing fn() and if the request was successful
        """
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
            List of the URL of the houses that are present in the navigation pages to scrape one by one
        """

        # checks if download directory exists
        download_dir = f"{config.FOTOCASA_IMG_DIR}-{location}-imgs"
        if utils.directory_exists(download_dir) == False:
            utils.create_directory(download_dir)

        # gets url conexion using Selenium
        driver = utils.get_selenium()
        driver.get(url)

        # accepts cookies
        acc = driver.find_element(by=By.CSS_SELECTOR,value='#App > div.re-SharedCmp > div > div > div > footer > div > button.sui-AtomButton.sui-AtomButton--primary.sui-AtomButton--solid.sui-AtomButton--center')
        utils.mini_wait()
        acc.click()

        # creates a list and stores each URL's house while scrolling down
        houses_to_visit = []
        last_page = False
        num_page = 0
        while last_page == False:
            num_page = num_page + 1
            utils.log(f"fotocasa - current page {num_page}")

            # evaluates location to take into account the tags including href
            if location == 'villaverde':

                # scrolls down and reads each house
                for scroll_i in range(config.FOTOCASA_SCROLL_LOCATION_PAGE):
                    ActionChains(driver).key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
                    utils.scroll_wait()

                    # evaluates the page number and reads the container to get house's urls
                    if num_page == 1:
                        main_content = driver.find_element(by=By.CSS_SELECTOR,value='#App > div.re-Page > div.re-SearchPage > main > div > div.re-SearchResult-wrapper > section')
                        try:
                            articles = main_content.find_elements(by=By.CSS_SELECTOR, value='article.re-CardPackPremium')
                        except Exception as e:
                            articles = main_content.find_elements(by=By.CSS_SELECTOR, value='article.re-CardPackAdvance')
                        
                        for article in articles:
                            # gets each article url
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
                                try:
                                    house_urls = article.find_element(by=By.CSS_SELECTOR, value='a.re-CardPackMinimal-slider').get_attribute('href')
                                    houses_to_visit.append(house_urls)
                                    self.__urls.update(dict.fromkeys(house_urls, location))
                                except Exception as e:
                                    utils.error(e)  
                        except Exception as e:
                            utils.log(e)
            
            # evaluates location to take into account the tags including href
            elif location == 'barrio-de-salamanca':

                for scroll_i in range(config.FOTOCASA_SCROLL_LOCATION_PAGE):
                    ActionChains(driver).key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
                    utils.scroll_wait()

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

            # when finishes, checks next page
            try:
                utils.mini_wait()
                items = driver.find_elements(by=By.CSS_SELECTOR, value='#App > div.re-Page > div.re-SearchPage.re-SearchPage--withMap > main > div > div.re-Pagination > ul > li.sui-MoleculePagination-item')
                for item in items:
                    url_next = item.find_element(by=By.CSS_SELECTOR, value='a')
                driver.get(url_next.get_attribute('href'))
            except Exception as e:
                utils.log(e)
                last_page = True

            # controls the maximun pages to process
            if config.FOTOCASA_NUM_PAGES_TO_READ == num_page:
                last_page = True
        
        utils.mini_wait()
        driver.quit()
        utils.log(f"Num of houses_to_visit: {len(houses_to_visit)}")
        return houses_to_visit


    def scrape(self, urls : list = None):
        """
        Scrapes the entire Fotocasa website or just a subset of it
        Creates a thread for navigation scraping and a thread for 
        house scraping; then synchronises both threads every
        X scraped URLs to backup the data

        Parameters
        ----------
        urls : list, opt
            List of the navigation pages URLs to scrape
        """
        utils.log("Starting Fotocasa dataset")

        # creates directory to save images
        if utils.directory_exists(config.FOTOCASA_IMG_DIR) == False:
            utils.create_directory(config.FOTOCASA_IMG_DIR)


        # creates URL using municiplity name only. Not necessary to invoke main page to get url-muniipality pair 
        url_call = urls[0]
        location = url_call.split("/")[-2]

        # invokes _scrape_navigation to get the complete list of houses to scrap
        utils.log("Obtaining list of houses")
        houses_list = self._scrape_navigation(url_call, location)
        
        # invokes _scrape_houses_details to process data from each house
        utils.log("Scrapping houses")
        houses = self._scrape_houses_details(location, houses_list)

        # creates dataframe and stores houses data
        utils.log('Merging the data')
        house_fields = ['id', 'url', 'title', 'location', 'price', 
        'm2', 'rooms', 'floor', 'num-photos', 'floor-plan', 'view3d', 'video', 
        'home-staging', 'description','photo_urls']
        utils.debug(f"Writing dataframe")
        df = pd.DataFrame(houses, columns=house_fields).drop_duplicates('id')

        # creates directory to store data if it does not exist
        if not utils.directory_exists(config.DATASET_DIR):
            utils.create_directory(config.DATASET_DIR)
    
        # writes dataframe into a CSV
        utils.log(f'Dumping dataset into {config.FOTOCASA_FILE}-{location}.csv')
        final_df = f"{config.FOTOCASA_FILE}-{location}.csv"
        df.to_csv(final_df, mode = 'a')
        utils.log(f'Dumped dataset into {config.FOTOCASA_FILE}-{location}.csv')
