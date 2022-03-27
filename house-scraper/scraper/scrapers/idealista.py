from .scraper_base import HouseScraper
from misc import config, utils
import re, csv, os
from concurrent.futures import ThreadPoolExecutor
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

class IdealistaScraper(HouseScraper):

    def _scrape_navigation(self, driver, url : str) -> list:
        """
        Scrapes the navigation pages for a location (given in the starting url).

        Parameters
        ----------
        driver : WebDriver
            Selenium webdriver to use
        url : str
            URL to start the scraping
        
        Returns
        -------
        List of the relative URL of the houses that are present in the navigation pages
        """
        driver.get(url)
        utils.mini_wait()
        houses_to_visit = list()
        
        while True:
            # browse all pages
            main_content = driver.find_element(by=By.CSS_SELECTOR, value='main#main-content > section.items-container')
            articles = main_content.find_elements(by=By.CSS_SELECTOR, value='article.item')
            driver.execute_script('arguments[0].scrollIntoView();', articles[0])
            for article in articles:
                # get each article url
                article_url = article.find_element(by=By.CSS_SELECTOR, 
                    value='div.item-info-container > a.item-link').get_attribute('href')
                houses_to_visit.append(article_url)
            try:
                next_page = main_content.find_element(by=By.CSS_SELECTOR, value='div.pagination > ul > li.next > a')
                utils.mini_wait()
                driver.execute_script('arguments[0].scrollIntoView();', next_page)
                utils.mini_wait()
                next_page.click()
            except NoSuchElementException as e:
                utils.warn(f'[{self.id}] {e}')
                utils.log(f'[{self.id}] No more pages to visit')
                break   # no more pages to navigate to
        return houses_to_visit

    def _get_house_features(self, anchors, features, extended_features, house : dict) -> dict:
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
        house['photos'] = photos

        map = False
        try: 
            anchors.find_element(by=By.CSS_SELECTOR, value='button.icon-plan')
            map = True  # checks if map button exists
        except NoSuchElementException as e: 
            pass    # map button does not exist
        house['map'] = 1 if map else 0

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

        house['m2'] = features.find_elements(by=By.CSS_SELECTOR, value='span')[0].find_element(
            by=By.CSS_SELECTOR, value='span').text
        house['rooms'] = features.find_elements(by=By.CSS_SELECTOR, value='span')[1].find_element(
            by=By.CSS_SELECTOR, value='span').text
        house['floor'] = features.find_elements(by=By.CSS_SELECTOR, value='span')[2].find_element(
            by=By.CSS_SELECTOR, value='span').text + features.find_elements(
                by=By.CSS_SELECTOR, value='span')[2].text
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

    def _scrape_house_page(self, driver, location: str, url : str) -> dict:
        """
        Scrapes a certain house detail page

        Parameters
        ----------
        driver : WebDriver
            Selenium webdriver to use
        location: str
            Location the house in in
        url : str
            URL to scrap
        
        Returns
        -------
        Dictionary with all the info on the house
        """
        try:
            house = {'id': '', 'url': '', 'title': '', 'location': '', 'sublocation': '',
                'price': '', 'm2': '', 'rooms': '', 'floor': '', 'photos': '', 'map': '',
                'view3d': '', 'video': '', 'home-staging': '', 'description': ''}
            driver.get(url)
            utils.mini_wait()
            main_content = driver.find_element(by=By.CSS_SELECTOR, value='main.detail-container > section.detail-info')

            house['id'] = int(re.search(r'\d+', url).group(0))
            house['url'] = driver.current_url
            house['title'] = main_content.find_element(by=By.CSS_SELECTOR, value='div.main-info__title > h1 > span').text
            house['location'] = location
            house['sublocation'] = main_content.find_element(by=By.CSS_SELECTOR, value='div.main-info__title > span > span').text
            house['price'] = main_content.find_element(by= By.CSS_SELECTOR, value='div.info-data > span.info-data-price > span').text
            
            anchors = main_content.find_element(by=By.CSS_SELECTOR, value='div.fake-anchors')
            features = main_content.find_element(by=By.CSS_SELECTOR, value='div.info-features')
            extended_features = main_content.find_element(by=By.CSS_SELECTOR, value='section#details > div.details-property')
            house = self._get_house_features(anchors, features, extended_features, house)
            
            house['description'] = main_content.find_element(by=By.CSS_SELECTOR, 
            value='div.commentsContainer > div.comment > div.adCommentsLanguage > p').text

            return house
        except NoSuchElementException as e:
            utils.error(f'[{self.id}] Something broke; the scraper has probably been detected')
            raise Exception('Scraper detected and blocked!')
        
    def _scrape_location(self, location : str, url : str):
        """
        Scrapes a location in idealista and puts all the info in the TMP folder
        of the project, under idealista/{location}.txt

        Parameters
        ----------
        location : str
            Name of the location to scrape
        url : str
            URL to be attached to the IDEALISTA_URL in order to scrape
        """
        _file = utils.create_file(os.path.join(config.TMP_DIR, self.id, location+'.csv'))
        house_fields = ['id', 'url', 'title', 'location', 'sublocation',
            'price', 'm2', 'rooms', 'floor', 'photos', 'map', 'view3d', 
            'video', 'home-staging', 'description']
        _writer = csv.DictWriter(_file, fieldnames=house_fields)
        _writer.writeheader()
        with utils.get_selenium() as driver:
            # browse all houses and get their info
            for house_url in self._scrape_navigation(driver, url):
                utils.wait()
                _writer.writerow(self._scrape_house_page(driver, location, house_url))
        
        _file.close()

    def scrape(self):
        """
        Scrapes the entire idealista website
        """
        
        utils.create_directory(os.path.join(config.TMP_DIR, self.id))
        locations_urls = dict()

        try:
            with utils.get_selenium() as driver:
                utils.mini_wait()
                driver.get(config.IDEALISTA_URL)
                utils.wait()
                locations_list = driver.find_elements(by=By.CSS_SELECTOR, 
                    value='section#municipality-search > div.locations-list > ul > li')
                driver.execute_script('arguments[0].scrollIntoView();', locations_list[0])
                # gets a pair of (province, url) for each location
                for location in locations_list:
                    loc_link = location.find_element(by=By.CSS_SELECTOR, value='a')
                    # bypass choosing a sublocation
                    locations_urls[loc_link.text] = re.sub(r'municipios$', '', loc_link.get_attribute('href'))
                utils.mini_wait()
        except Exception as e: 
            utils.error(f'[{self.id}]: {e}')
        
        # concurrent scrape of all provinces, using 5 threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            for location, url in locations_urls.items():
                executor.submit(self._scrape_location, location, url)