"""
Idealista web scraper. Launches a thread to scrape the 
navigation - collects the houses URLs - and a thread to
scrape the houses - getting the details of each house.

Includes saving of state objects and dataframe periodically
so it can be relaunched  if it fails.
"""

import atexit
import os
import pickle
import re
import threading
from queue import PriorityQueue, Queue
from time import sleep

import pandas as pd
from misc import captcha_solver, config, utils
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from .scraper_base import HouseScraper


class IdealistaScraper(HouseScraper):

    # state holding objects
    __scrape_navigation = True
    __scrape_houses = True
    __navigations_to_visit = PriorityQueue()
    __houses_to_visit = Queue()
    __houses_visited = list()

    # config for the periodic backup
    __urls_before_cleanup = config.IDEALISTA_BACKUP_AFTER
    __cleaner_semaphore = threading.Semaphore(value=__urls_before_cleanup)
    __cleaner_signal = threading.Event()

    def __init__(self, id: str):
        super().__init__(id)
        atexit.register(self.cleanup)   # at exit, backup

        if not utils.directory_exists(config.IDEALISTA_TMP):
            utils.create_directory(config.IDEALISTA_TMP)

        # recover the pickled state holding objects
        if utils.file_exists(os.path.join(config.IDEALISTA_TMP, 'navigations-to-scrap.pkl')):
            with open(os.path.join(config.IDEALISTA_TMP, 'navigations-to-scrap.pkl'), 'rb') as file:
                for nav in pickle.load(file):
                    self.__navigations_to_visit.put(nav)
                utils.log(f'{list(self.__navigations_to_visit.queue)}')
                self.__scrape_navigation = not self.__navigations_to_visit.empty()
        if utils.file_exists(os.path.join(config.IDEALISTA_TMP, 'houses-to-scrap.pkl')):
            with open(os.path.join(config.IDEALISTA_TMP, 'houses-to-scrap.pkl'), 'rb') as file:
                for house in pickle.load(file):
                    self.__houses_to_visit.put(house)
                self.__scrape_houses = not self.__houses_to_visit.empty()
        if utils.file_exists(os.path.join(config.IDEALISTA_TMP, 'visited-houses.pkl')):
            with open(os.path.join(config.IDEALISTA_TMP, 'visited-houses.pkl'), 'rb') as file:
                self.__houses_visited = pickle.load(file)

    def cleanup(self):
        """
        Backs up the state holding objects into pickle files
        """
        utils.log(f'Back-upping data')
        with open(os.path.join(config.IDEALISTA_TMP, 'navigations-to-scrap.pkl'), 'wb') as file:
            pickle.dump(list(self.__navigations_to_visit.queue),
                        file, pickle.HIGHEST_PROTOCOL)
        with open(os.path.join(config.IDEALISTA_TMP, 'houses-to-scrap.pkl'), 'wb') as file:
            pickle.dump(list(self.__houses_to_visit.queue),
                        file, pickle.HIGHEST_PROTOCOL)
        with open(os.path.join(config.IDEALISTA_TMP, 'visited-houses.pkl'), 'wb') as file:
            pickle.dump(self.__houses_visited, file, pickle.HIGHEST_PROTOCOL)

    def try_page(self, driver, fn):
        """
        Tries to access the element provided in fn (find_element() usually) and
        solves any errors and captchas in its way.

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
        retries = 0
        while not madeit:
            try:
                result = fn()
                madeit = True
            except NoSuchElementException:
                try:
                    #utils.wait() if utils.flip_coin() else utils.mega_wait()
                    status_code = utils.get_http_code(driver.current_url)
                    utils.warn(
                        f'[{self.id}] Error {status_code}, trying to solve it...')
                    if status_code == 403 or captcha_solver.check(driver):
                        captcha_solver.solve(driver)
                    elif status_code == 404:
                        utils.warn(
                            f'[{self.id}] Error 404 in {driver.current_url}')
                        return None, False
                    else:
                        retries += 1
                        if retries > config.IDEALISTA_MAX_RETRIES:
                            return None, False
                        utils.mega_wait()
                        driver.refresh()
                except:
                    utils.error(
                        f'[{self.id}] Error retrieving {driver.current_url}')
                    retries += 1
                    if retries > config.IDEALISTA_MAX_RETRIES:
                        return None, False
                    utils.mega_wait()
                    driver.refresh()
                madeit = False
        return result, True

    def _scrape_navigation(self, driver, url: str, priority: int = 0):
        """
        Scrapes the navigation page given in the URL for houses URLs.
        Updates the state holding objects with new houses URLs and new
        pages to navigate

        Parameters
        ----------
        driver
            Selenium driver
        url : str
            URL to scrape
        priority : int, opt
            The priority of the URL and subsequent navigation pages. Less is better
        """
        utils.mini_wait()
        driver.get(url)

        # see how much we have to wait
        utils.wait() if utils.flip_coin() else utils.mini_wait()

        # browse all pages
        main_content, success = self.try_page(driver, lambda: driver.find_element(by=By.CSS_SELECTOR,
                                                                                  value='main#main-content > section.items-container'))
        if not success:
            utils.warn(f'[{self.id}] Page unavailable: {url}')
            return
        articles = main_content.find_elements(
            by=By.CSS_SELECTOR, value='article.item')
        for article in articles:
            # get each article url
            article_url = article.find_element(by=By.CSS_SELECTOR,
                                               value='div.item-info-container > a.item-link').get_attribute('href')
            self.__houses_to_visit.put(article_url)
        try:
            next_page = main_content.find_element(
                by=By.CSS_SELECTOR, value='div.pagination > ul > li.next > a')
            next_page_link = next_page.get_attribute('href')
            self.__navigations_to_visit.put((priority, next_page_link))
        except NoSuchElementException as e:
            utils.log(f'[{self.id}] No more pages to visit')
            utils.warn(f'[{self.id}] {e.msg}')

    def _get_house_features(self, driver, anchors, features, house: dict) -> dict:
        """
        Gets some features from the house: number of photos, if there is a map, video and 3D view 
        available in the web, if there exists a home staging feature, the m2, number of rooms and
        the floor the house is in. Download the floor plan if it exists.

        Parameters
        ----------
        anchors : WebElement
            the div where the photos, view3D, etc are located
        features : WebElement
            the div where the main (basic) features are located
        house : dict
            Dictionary to append the information to

        Returns
        -------
        Updated house dictionary
        """
        photos = 0
        try:
            photos_text = anchors.find_element(
                by=By.CSS_SELECTOR, value='button.icon-no-pics > span').text
            # '10 fotos' -> 10
            photos = int(re.search(r'\d+', photos_text).group(0))
        except NoSuchElementException as e:
            pass    # no photos
        house['num-photos'] = photos

        map = False
        try:
            map_button = anchors.find_element(
                by=By.CSS_SELECTOR, value='button.icon-plan')

            # get image
            map_button.click()
            utils.mini_wait()

            close_button = driver.find_element(by=By.CSS_SELECTOR, value='div#gallery ' +
                                               'div.rs-gallery-hud > header.rs-gallery-header > span.icon-close')
            map_img = driver.find_element(by=By.CSS_SELECTOR,
                                          value='div#gallery > main.rs-gallery-container div.image-gallery-content' +
                                          ' div.image-gallery-slide.center > figure.item-gallery > img')

            map_url = map_img.get_attribute('src')
            utils.download_image(map_url, os.path.join(
                config.IDEALISTA_MAPS, str(house['id']) + '.jpg'))

            close_button.click()
            utils.mini_wait()

            map = True  # checks if map button exists
        except NoSuchElementException as e:
            pass    # map button does not exist
        house['floor-plan'] = 1 if map else 0

        view3d = False
        try:
            anchors.find_element(by=By.CSS_SELECTOR,
                                 value='button.icon-3d-tour-outline')
            view3d = True  # checks if view3d button exists
        except NoSuchElementException as e:
            pass    # view3d button does not exist
        house['view3d'] = 1 if view3d else 0

        video = False
        try:
            anchors.find_element(by=By.CSS_SELECTOR,
                                 value='button.icon-videos')
            video = True  # checks if video button exists
        except NoSuchElementException as e:
            pass    # video button does not exist
        house['video'] = 1 if video else 0

        staging = False
        try:
            anchors.find_element(by=By.CSS_SELECTOR,
                                 value='button.icon-homestaging')
            staging = True  # checks if staging button exists
        except NoSuchElementException as e:
            pass    # staging button does not exist
        house['home-staging'] = 1 if staging else 0

        house_features = features.find_elements(
            by=By.CSS_SELECTOR, value='div.info-features > span')
        if len(house_features) >= 1:
            house['m2'] = house_features[0].find_element(
                by=By.CSS_SELECTOR, value='span').text
        if len(house_features) >= 2:
            maybe_rooms = house_features[1].find_element(
                by=By.CSS_SELECTOR, value='span').text
            if re.search(r'\d+ hab.', maybe_rooms):
                house['rooms'] = maybe_rooms
            else:
                house['floor'] = maybe_rooms
        if len(house_features) >= 3:
            house['floor'] = house_features[2].text
        if not re.search(r'Planta', house['floor']):
            house['floor'] = 'Sin planta'

        return house

    def _scrape_house_page(self, driver, url: str):
        """
        Scrapes a certain house detail page. Updates the state holding objects.

        Parameters
        ----------
        driver
            Selenium driver
        url : str
            URL to scrap
        """
        try:
            house = {'id': '', 'url': '', 'title': '', 'location': '', 'price': '',
                     'm2': '', 'rooms': '', 'floor': '', 'num-photos': '', 'floor-plan': '', 'view3d': '',
                     'video': '', 'home-staging': '', 'description': ''}
            utils.log(f'[idealista] Scraping {url}')
            utils.mini_wait()
            driver.get(url)
            utils.mini_wait()
            main_content, success = self.try_page(driver, lambda: driver.find_element(
                by=By.CSS_SELECTOR, value='main.detail-container > section.detail-info'))

            if not success:
                utils.warn(f'[{self.id}] Page unavailable: {url}')
                return

            house['id'] = int(re.search(r'\d+', url).group(0))
            house['url'] = driver.current_url
            house['title'] = main_content.find_element(
                by=By.CSS_SELECTOR, value='div.main-info__title > h1 > span').text
            house['location'] = main_content.find_element(
                by=By.CSS_SELECTOR, value='div.main-info__title > span > span').text
            house['price'] = int(main_content.find_element(by=By.CSS_SELECTOR,
                                                           value='div.info-data > span.info-data-price > span').text.replace('.', ''))

            anchors = main_content.find_element(
                by=By.CSS_SELECTOR, value='div.fake-anchors')
            house = self._get_house_features(
                driver, anchors, main_content, house)

            house['description'] = main_content.find_element(by=By.CSS_SELECTOR,
                                                             value='div.commentsContainer > div.comment > div.adCommentsLanguage > p').text.rstrip()
            house['description'] = house['description'].replace(
                '\n', ' ').rstrip()

            if house['num-photos'] > 0:
                photo_container = driver.find_element(
                    by=By.CSS_SELECTOR, value='div#multimedia-container > div#main-multimedia')

                # check if there is a button of 'show all the photos'
                photo_buttons = photo_container.find_elements(
                    by=By.CSS_SELECTOR, value='div.more')
                if len(photo_buttons) > 0:
                    photo_buttons[0].click()

                utils.mini_wait()

                photos = photo_container.find_elements(
                    by=By.CSS_SELECTOR, value='div.image > img')
                house['photo_urls'] = [photo.get_attribute(
                    'data-ondemand-img') for photo in photos]

            self.__houses_visited.append(house)
        except NoSuchElementException as e:
            utils.error(f'[{self.id}] Something happened!')
            utils.error(f'Exception: {e.msg}')
        except:
            utils.error(f'[{self.id}] Something happened!')

    def _scrape_first_time_nav(self):
        """
        Creates a new Selenium driver and gets the URLs of the navigation pages of all the
        provinces/regions. Updates the state holding objects
        """
        try:
            with utils.get_selenium() as driver:
                utils.mini_wait()
                driver.get(config.IDEALISTA_URL)
                utils.mini_wait()
                _, success = self.try_page(driver, lambda: driver.find_element(
                    by=By.CSS_SELECTOR, value='section#municipality-search'))

                if not success:
                    utils.warn(
                        f'[{self.id}] Page unavailable: {config.IDEALISTA_URL}')
                    return

                locations_list = driver.find_elements(by=By.CSS_SELECTOR,
                                                      value='section#municipality-search > div.locations-list > ul > li')
                driver.execute_script(
                    'arguments[0].scrollIntoView();', locations_list[0])
                # gets a pair of (province, url) for each location
                for location in locations_list:
                    loc_link = location.find_element(
                        by=By.CSS_SELECTOR, value='a')
                    loc_number = int(location.find_element(
                        by=By.CSS_SELECTOR, value='p').text.replace('.', ''))
                    # bypass choosing a sublocation
                    self.__navigations_to_visit.put(
                        (loc_number, re.sub(r'municipios$', '', loc_link.get_attribute('href'))))
                utils.mini_wait()
        except Exception as e:
            utils.error(f'[{self.id}]: {e.msg}')

    def start_navigating(self):
        """
        Begins navigating the URLs provided by the state holding objects
        """
        with utils.get_selenium() as driver:
            try:
                while not self.__navigations_to_visit.empty():
                    if not self.__cleaner_semaphore.acquire(blocking=True, timeout=100):
                        # reached maximum URLs visited before dump
                        self.__cleaner_signal.set()
                        self.__cleaner_semaphore.acquire(
                            blocking=True, timeout=0)
                    navigation = self.__navigations_to_visit.get()
                    self._scrape_navigation(
                        driver, navigation[1], navigation[0])
                self.__scrape_navigation = False
            except:
                utils.error(f'[{self.id}] Error while navigating')

    def start_house_scraping(self):
        """
        Launches some workers that will scrape the houses
        """
        threads = [threading.Thread(target=self.house_scraper)
                   for _ in range(config.MAX_WORKERS)]
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]

    def house_scraper(self):
        """
        Begins scraping the house URLs provided by the state holding objects
        """
        with utils.get_selenium() as driver:
            try:
                utils.mini_wait()
                while self.__scrape_houses:
                    try:
                        if not self.__cleaner_semaphore.acquire(blocking=True, timeout=100):
                            self.__cleaner_signal.set()
                            self.__cleaner_semaphore.acquire(
                                blocking=True, timeout=0)
                        house = self.__houses_to_visit.get(timeout=500)
                    except Exception:
                        # navigation scraped and houses scraped
                        if not self.__scrape_navigation:
                            self.__scrape_houses = False
                            continue
                    self._scrape_house_page(driver, house)
                    utils.mega_wait() if utils.flip_coin() else utils.wait(
                    ) if utils.flip_coin() else utils.mini_wait()
            except:
                utils.error(f'[{self.id}] Error while scraping')

    def dump_houses(self):
        """
        Dumps the houses info into a CSV file
        """
        # mix all the data, keep unique IDs
        utils.log(f'Dumping houses CSV')
        house_fields = ['id', 'url', 'title', 'location', 'price',
                        'm2', 'rooms', 'floor', 'num-photos', 'floor-plan', 'view3d', 'video',
                        'home-staging', 'description', 'photo_urls']
        df = pd.DataFrame(self.__houses_visited,
                          columns=house_fields).drop_duplicates('id')

        if not utils.directory_exists(config.DATASET_DIR):
            utils.create_directory(config.DATASET_DIR)
        if utils.file_exists(config.IDEALISTA_FILE):
            existing_df = pd.read_csv(config.IDEALISTA_FILE)
            df = pd.concat([df, existing_df]).drop_duplicates('id')
        utils.log(f'Dumping dataset into {config.IDEALISTA_FILE}')
        df.to_csv(config.IDEALISTA_FILE, encoding='utf-8',
                  index=False, header=True)
        self.__houses_visited.clear()
        utils.log(f'Dumped dataset of {df.shape} into {config.IDEALISTA_FILE}')

    def scrape(self, urls: list = None):
        """
        Scrapes the entire idealista website or just a subset of it
        Creates a thread for navigation scraping and a thread for 
        house scraping; then synchronises both threads every
        X scraped URLs to backup the data

        Parameters
        ----------
        urls : list, opt
            List of the navigation pages URLs to scrape
        """
        try:
            utils.create_directory(config.IDEALISTA_MAPS)
            nav_thread = None

            if self.__scrape_navigation:
                if self.__navigations_to_visit.empty():
                    if not urls:
                        utils.log(
                            '[idealista] Started navigating all idealista')
                        self._scrape_first_time_nav()
                    else:
                        utils.log(
                            f'[idealista] Started navigating only {len(urls)} idealista locations')
                        for i, url in enumerate(urls):
                            self.__navigations_to_visit.put((i, url))
                nav_thread = threading.Thread(target=self.start_navigating)

            houses_thread = None
            if self.__scrape_houses:
                houses_thread = threading.Thread(
                    target=self.start_house_scraping)

            if nav_thread:
                nav_thread.start()
            if houses_thread:
                houses_thread.start()

            while ((nav_thread.is_alive() if nav_thread else False) or
                    (houses_thread.is_alive() if houses_thread else False)):
                self.__cleaner_signal.wait()
                sleep(config.SYNCHRO_MAX_WAIT)

                self.dump_houses()
                self.cleanup()

                self.__cleaner_signal.clear()
                self.__cleaner_semaphore.release(n=self.__urls_before_cleanup)
        except:
            utils.error(f'[idealista] Something went wrong (?)')
        finally:
            # whatever happens, backup and dump!
            # final backup and dump
            self.cleanup()
            self.dump_houses()
