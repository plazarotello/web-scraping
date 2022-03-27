from misc import config, utils
from scrapers.scraper_base import HouseScraper
from scrapers.scraper_factory import ScraperFactory

from time import time, gmtime, strftime, sleep
import threading

def init_tmp():
    """
    Initializes the temporary folder to dump the data on
    """
    utils.create_directory(config.TMP_DIR)


def scrape_web(scraper : HouseScraper):
    """
    Monitors the elapsed time needed to scrape a real state listing web

    Parameters
    ----------
    scraper : HouseScraper
        The scraper object that is going to scrape the web
    """
    start_time = time()
    sleep(2)
    end_time = time()
    elapsed_seconds = end_time - start_time
    print(f'[{scraper.id}] Elapsed time: {strftime("%H:%M:%S", gmtime(elapsed_seconds))}')


def main():
    """
    Launches several threads to scrape multiple real state listing webs; then joins 
    the results in a single CSV file
    """

    print('Starting web scraping......')
    init_tmp()
    scrapers_ids = ['idealista', 'fotocasa', 'pisos.com', 'kasaz']
    scraper_threads = list()
    for id in scrapers_ids:
        scraper_thread = threading.Thread(target=scrape_web, args=(ScraperFactory.create_scraper(id),))
        scraper_threads.append(scraper_thread)
        scraper_thread.start()
    
    for scraper_thread in scraper_threads:
        scraper_thread.join()
    print('......Finished web scraping')
    print('...........................')
    print('Joining results............')
    # join results
    print('.....Created final CSV file')

if __name__ == '__main__':
    #main()
    init_tmp()
    ScraperFactory.create_scraper('idealista').scrape()