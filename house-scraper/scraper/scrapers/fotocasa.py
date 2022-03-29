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


    def scrape(self):
            """
            Scrapes the entire idealista website
            """
            with utils.create_file(config.TMP_DIR, self.id + '.csv') as _file:
                writer = csv.DictWriter(_file,fieldnames=['url', 'location'])
                '''
                self._scrape_houses_urls()
                writer.writeheader()
                for url, location in self.__urls.items():
                    writer.writerow([url, location])
'''
            #houses = self._scrape_houses_details()

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

