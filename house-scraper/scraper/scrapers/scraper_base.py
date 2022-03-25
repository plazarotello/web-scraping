import requests
import os
from bs4 import BeautifulSoup
from time import sleep
from misc import config, utils

class HouseScraper():
    """
    Class used to represent a scraper that will crawl through a single 
    real state listing web

    ...

    Attributes
    ----------
    id : str
        identifier for the scraper
    
    Methods
    -------
    scrape()
        Crawls through the web

    """

    def __init__(self, id : str):
        self.id = id
    
    def scrape(self): raise NotImplementedError
    def __parse(self): raise NotImplementedError

    def _create_tmp_file(*dirs : str, file_name : str):
        """
        Creates a file open for writing. Overrides whatever was on that file.

        Parameters
        ----------
        *dirs : str
            Directories to concatenate in which the file is going to be created
        file_name : str
            Name of the file to be created

        Returns
        -------
        file handler to write on
        """
        return(utils.create_file(os.path.join(config.TMP_DIR, *dirs), file_name))

    def _create_tmp_dir(*dir_names : str):
        """
        Creates a folder in the specified path. Deletes the folder and makes one 
        anew if it existed.

        Parameters
        ----------
        *dir_names : str
            Directories to concatenate
        """
        utils.create_directory(os.path.join(config.TMP_DIR, *dir_names))

    def _get_url(url : str, cookies = None, retries=5) -> BeautifulSoup:
        """
        Tries to get a Beautiful Soup from a url. If it fails, makes multiple
        attempts before giving up

        Parameters
        ----------
        url : str
            URL to get
        retries : int, optional
            Number of retries before giving up

        Raises
        ------
        Exception
            If it can't get the URL after multiple attempts
        """

        # tries to open the url multiple times before giving up
        for retry in range(retries+1):
            try:
                r = requests.get(url, headers=config.HEADERS, cookies=cookies)
                r.raise_for_status()    # if returned code is unsuccesful, raise error
                html = r.content
            except (requests.HTTPError, requests.ConnectionError) as e:
                print(f'Error in {url}: {e}')
                # sleeps an increasing number of seconds between attempts
                sleep(0.5 + 0.5*retry)
                continue

            # if there are no errors opening the URL, returns the soup
            return BeautifulSoup(html, 'html.parser')
        
        raise Exception(f'Unable to reach {url}')