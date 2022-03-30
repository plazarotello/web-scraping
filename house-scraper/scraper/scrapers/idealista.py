import os
import atexit
import re
from queue import Queue
import pickle
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from misc import config, utils, captcha_solver
from .scraper_base import HouseScraper


class IdealistaScraper(HouseScraper):

    __scrape_navigation = True
    __scrape_houses = True
    __navigations_to_visit = Queue()
    __houses_to_visit = Queue()
    __houses_visited = list()

    def __init__(self, id: str):
        super().__init__(id)
        atexit.register(self.cleanup)
        if not utils.directory_exists(config.IDEALISTA_TMP):
            utils.create_directory(config.IDEALISTA_TMP)
        if utils.file_exists(os.path.join(config.IDEALISTA_TMP, 'state.pkl')):
            with open(os.path.join(config.IDEALISTA_TMP, 'state.pkl'), 'rb') as file:
                state_data = pickle.load(file)
            self.__scrape_navigation = state_data['scrape-nav']
            self.__scrape_houses = state_data['scrape-houses']
            self.__navigations_to_visit = state_data['nav-to-scrap']
            self.__houses_to_visit = state_data['houses-to-scrap']
            self.__houses_visited = state_data['houses-scraped']
        
    def cleanup(self):
        state_data = dict()
        state_data['houses-scraped'] = self.__houses_visited
        state_data['nav-to-scrap'] = self.__navigations_to_visit
        state_data['houses-to-scrap'] = self.__houses_to_visit
        state_data['scrape-nav'] = not self.__navigations_to_visit.empty()
        state_data['scrape-houses'] = not self.__houses_to_visit.empty()
        with open(os.path.join(config.IDEALISTA_TMP, 'state.pkl'), 'wb') as file:
            pickle.dump(state_data, file, pickle.HIGHEST_PROTOCOL)

    def try_page(self, driver, fn):
        madeit = False
        while not madeit:
            try:
                result = fn()
                madeit = True
            except NoSuchElementException:
                try:
                    #utils.wait() if utils.flip_coin() else utils.mega_wait()
                    utils.warn(f'[{self.id}] Error 403, trying to solve it...')
                    if captcha_solver.check(driver): captcha_solver.solve(driver)
                    elif not utils.get_http_code(driver.current_url) in [200, 403]:
                        utils.mega_wait()
                        driver.refresh()
                except Exception:
                    utils.mega_wait()
                    driver.refresh()
                madeit=False
        return result

    def _scrape_navigation(self, url : str):
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

        # see how much we have to wait
        utils.mini_wait() if utils.flip_coin() else utils.wait()

        # browse all pages
        main_content = self.try_page(driver, lambda : driver.find_element(by=By.CSS_SELECTOR, 
                value='main#main-content > section.items-container'))

        articles = main_content.find_elements(by=By.CSS_SELECTOR, value='article.item')
        for article in articles:
            # get each article url
            article_url = article.find_element(by=By.CSS_SELECTOR, 
                value='div.item-info-container > a.item-link').get_attribute('href')
            self.__houses_to_visit.put(article_url)
        try:
            next_page = main_content.find_element(by=By.CSS_SELECTOR, value='div.pagination > ul > li.next > a')
            next_page_link = next_page.get_attribute('href')
            self.__navigations_to_visit.put(next_page_link)
        except NoSuchElementException as e:
            utils.log(f'[{self.id}] No more pages to visit')
            utils.warn(f'[{self.id}] {e.msg}')
        
        utils.mini_wait()
        driver.quit()

    def _get_house_features(self, driver, anchors, features, extended_features, house : dict) -> dict:
        """
        Gets some features from the house: number of photos, if there is a map, video and 3D view 
        available in the web, if there exists a home staging feature, the m2, number of rooms and
        the floor the house is in.

        Parameters
        ----------
        anchors : WebElement
            the div where the photos, view3D, etc are located
        features : WebElement
            the div where the main (basic) features are located
        extended_features : WebElement
            the div where the extended features are located
        house : dict
            Dictionary to append the information to
        
        Returns
        -------
        Updated house dictionary
        """

        photos = 0
        try:
            photos_text = anchors.find_element(by=By.CSS_SELECTOR, value='button.icon-no-pics > span').text
            photos = int(re.search(r'\d+', photos_text).group(0))   # '10 fotos' -> 10
        except NoSuchElementException as e:
            pass    # no photos
        house['num-photos'] = photos

        map = False
        try: 
            map_button = anchors.find_element(by=By.CSS_SELECTOR, value='button.icon-plan')
            
            # get image
            utils.mini_wait()
            map_button.click()
            utils.mini_wait()
            
            close_button = driver.find_element(by=By.CSS_SELECTOR, value='div#gallery '+
                'div.rs-gallery-hud > header.rs-gallery-header > span.icon-close')
            map_img = driver.find_element(by=By.CSS_SELECTOR, 
                value='div#gallery > main.rs-gallery-container div.image-gallery-content' +
                    ' div.image-gallery-slide.center > figure.item-gallery > img')
            
            map_url = map_img.get_attribute('src')
            utils.download_image(map_url, os.path.join(config.IDEALISTA_MAPS, str(house['id']) + '.jpg'))

            close_button.click()
            utils.mini_wait()

            map = True  # checks if map button exists
        except NoSuchElementException as e: 
            pass    # map button does not exist
        house['floor-plan'] = 1 if map else 0

        view3d = False
        try: 
            anchors.find_element(by=By.CSS_SELECTOR, value='button.icon-3d-tour-outline')
            view3d = True  # checks if view3d button exists
        except NoSuchElementException as e: 
            pass    # view3d button does not exist
        house['view3d'] = 1 if view3d else 0

        video = False
        try: 
            anchors.find_element(by=By.CSS_SELECTOR, value='button.icon-videos')
            video = True  # checks if video button exists
        except NoSuchElementException as e: 
            pass    # video button does not exist
        house['video'] = 1 if video else 0

        staging = False
        try: 
            anchors.find_element(by=By.CSS_SELECTOR, value='button.icon-homestaging')
            staging = True  # checks if staging button exists
        except NoSuchElementException as e: 
            pass    # staging button does not exist
        house['home-staging'] = 1 if staging else 0

        house_features = features.find_elements(by=By.CSS_SELECTOR, value='div.info-features > span')
        if len(house_features) >= 1:
            house['m2'] = house_features[0].find_element(by=By.CSS_SELECTOR, value='span').text
        if len(house_features) >= 2:
            maybe_rooms = house_features[1].find_element(by=By.CSS_SELECTOR, value='span').text
            if re.search(r'\d+ hab.', maybe_rooms):
                house['rooms'] = maybe_rooms
            else:
                house['floor'] = maybe_rooms
        if len(house_features) >= 3:
            house['floor'] = house_features[2].find_element(by=By.CSS_SELECTOR, value='span'
                ).text + house_features[2].text
        if not re.search(r'Planta', house['floor']):
            house['floor'] = 'Sin planta'
        
        # TODO Get info on house, building, equipment and energy features
        try:
            basic_features = extended_features.find_element(by=By.XPATH, 
                value='// h3[contains(text(), "Características básicas")]/following-sibling::div/child::ul')
        except NoSuchElementException as e:
            pass    # no basic features
        try:
            building_features = extended_features.find_element(by=By.XPATH, 
            value='// h3[contains(text(), "Edificio")]/following-sibling::div/child::ul')
        except NoSuchElementException as e:
            pass    # no building features
        try:
            equipment_features = extended_features.find_element(by=By.XPATH, 
            value='// h3[contains(text(), "Equipamiento")]/following-sibling::div/child::ul')
        except NoSuchElementException as e:
            pass    # no equipment features
        try:
            energy_features = extended_features.find_element(by=By.XPATH, 
            value='// h3[contains(text(), "Certificado energético")]/following-sibling::div/child::ul')
        except NoSuchElementException as e:
            pass    # no energy features

        return house

    def _scrape_house_page(self, url : str):
        """
        Scrapes a certain house detail page

        Parameters
        ----------
        url : str
            URL to scrap
        
        Returns
        -------
        Dictionary with all the info on the house
        """
        with utils.get_selenium() as driver:
            try:
                house = {'id': '', 'url': '', 'title': '', 'location': '', 'price': '', 
                'm2': '', 'rooms': '', 'floor': '', 'num-photos': '', 'floor-plan': '','view3d': '', 
                'video': '', 'home-staging': '', 'description': ''}
                utils.log(f'[idealista] Scraping {url}')
                utils.mini_wait()
                driver.get(url)
                main_content = self.try_page(driver, lambda: driver.find_element(by=By.CSS_SELECTOR, value='main.detail-container > section.detail-info'))

                house['id'] = int(re.search(r'\d+', url).group(0))
                house['url'] = driver.current_url
                house['title'] = main_content.find_element(by=By.CSS_SELECTOR, value='div.main-info__title > h1 > span').text
                house['location'] = main_content.find_element(by=By.CSS_SELECTOR, value='div.main-info__title > span > span').text
                house['price'] = int(main_content.find_element(by= By.CSS_SELECTOR, 
                    value='div.info-data > span.info-data-price > span').text.replace('.', ''))
                
                anchors = main_content.find_element(by=By.CSS_SELECTOR, value='div.fake-anchors')
                extended_features = main_content.find_element(by=By.CSS_SELECTOR, value='section#details > div.details-property')
                house = self._get_house_features(driver, anchors, main_content, extended_features, house)
                
                house['description'] = main_content.find_element(by=By.CSS_SELECTOR, 
                value='div.commentsContainer > div.comment > div.adCommentsLanguage > p').text.strip()

                self.__houses_visited.append(house)
            except NoSuchElementException as e:
                utils.error(f'[{self.id}] Something happened!')
                utils.error(f'Exception: {e.msg}')
        
    def _scrape_first_time_nav(self):
        try:
            with utils.get_selenium() as driver:
                utils.mini_wait()
                driver.get(config.IDEALISTA_URL)
                utils.mini_wait()
                _ = self.try_page(driver, lambda: driver.find_element(by=By.CSS_SELECTOR, value='section#municipality-search'))
                locations_list = driver.find_elements(by=By.CSS_SELECTOR, 
                            value='section#municipality-search > div.locations-list > ul > li')
                driver.execute_script('arguments[0].scrollIntoView();', locations_list[0])
                # gets a pair of (province, url) for each location
                for location in locations_list:
                    loc_link = location.find_element(by=By.CSS_SELECTOR, value='a')
                    # loc_number = int(location.find_element(by=By.CSS_SELECTOR, value='p').text.replace('.', ''))
                    # bypass choosing a sublocation
                    self.__navigations_to_visit.put(re.sub(r'municipios$', '', loc_link.get_attribute('href')))
                utils.mini_wait()
        except Exception as e:
            utils.error(f'[{self.id}]: {e.msg}')

    def start_navigating(self):
        # concurrent scrape of all provinces, using multiple threads
        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            # max_locations_before_wait = 20
            # loc_number = 0
            futures = []
            while self.__scrape_navigation:
                try:
                    navigation = self.__navigations_to_visit.get(timeout=500)
                except Exception:
                    # everything has been scraped
                    if all(scrap.done() for scrap in futures):
                        self.__scrape_navigation = False
                        continue

                futures.append(executor.submit(self._scrape_navigation, navigation))
                # loc_number = loc_number+1
                # if loc_number >= max_locations_before_wait:
                #     loc_number = 0
                #     for _ in range(config.MAX_WORKERS):
                #         executor.submit(lambda: utils.mega_wait())

    def start_house_scraping(self) -> list:
        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            max_houses_before_wait = 20
            house_number = 0
            futures = []
            while self.__scrape_houses:
                try:
                    house = self.__houses_to_visit.get(timeout=500)
                except Exception:
                    # navigation scraped and houses scraped
                    if all(scrap.done() for scrap in futures) and not self.__scrape_navigation:
                        self.__scrape_houses = False
                        continue
                
                futures.append(executor.submit(self._scrape_house_page, house))
                house_number = house_number+1
                if house_number >= max_houses_before_wait:
                    house_number = 0
                    for _ in range(config.MAX_WORKERS):
                        executor.submit(lambda : utils.mega_wait())

    def scrape(self):
        """
        Scrapes the entire idealista website
        """
        utils.create_directory(config.IDEALISTA_MAPS)
        nav_thread = None
        if self.__scrape_navigation:
            if self.__navigations_to_visit.empty():
                self._scrape_first_time_nav()
            nav_thread = threading.Thread(target=self.start_navigating)
        
        houses_thread = None
        if self.__scrape_houses:
            houses_thread = threading.Thread(target=self.start_house_scraping)
        
        if nav_thread: nav_thread.start()
        if houses_thread: houses_thread.start()

        if nav_thread: nav_thread.join()
        if houses_thread: houses_thread.join()

        # mix all the data, keep unique IDs
        utils.log('Merging the data')
        house_fields = ['id', 'url', 'title', 'location', 'price', 
        'm2', 'rooms', 'floor', 'num-photos', 'floor-plan', 'view3d', 'video', 
        'home-staging', 'description']
        df = pd.DataFrame(self.__houses_visited, columns=house_fields).drop_duplicates('id')

        if not utils.directory_exists(config.DATASET_DIR):
            utils.create_directory(config.DATASET_DIR)
        utils.log(f'Dumping dataset into {config.IDEALISTA_FILE}')
        df.to_csv(config.IDEALISTA_FILE)
        utils.log(f'Dumped dataset into {config.IDEALISTA_FILE}')
