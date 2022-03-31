import os
import sys
import argparse
import threading
from time import gmtime, strftime, time

from misc import config, utils
from scrapers.scraper_base import HouseScraper
from scrapers.scraper_factory import ScraperFactory


def init_tmp_folder(scrapers : list, delete_all : bool = False):
    """
    Initializes the temporary folder to dump the data on
    """
    if delete_all:
        utils.create_directory(config.TMP_DIR)
        return
    elif not utils.directory_exists(config.TMP_DIR):
        utils.create_directory(config.TMP_DIR)
        return
    else:
        directories = utils.get_directories(config.TMP_DIR)
        for id in scrapers:
            if os.path.join(config.TMP_DIR, id) in directories:
                # don't delete the scrapers we want to keep
                directories.remove(os.path.join(config.TMP_DIR, id))
        for directory in directories:
            utils.delete_directory(directory)



def scrape_web(scraper : HouseScraper, urls : list = None):
    """
    Monitors the elapsed time needed to scrape a real estate listing web

    Parameters
    ----------
    scraper : HouseScraper
        The scraper object that is going to scrape the web
    """
    start_time = time()
    scraper.scrape(urls)
    end_time = time()
    elapsed_seconds = end_time - start_time
    utils.log(f'[{scraper.id}] Elapsed time: {strftime("%H:%M:%S", gmtime(elapsed_seconds))}')


def main(scrapers_ids : list, urls : dict):
    """
    Launches several threads to scrape multiple real estate listing webs; then joins 
    the results in a single CSV file

    Parameters
    ----------
    scrapers_ids : list
        List of the selected pages' IDs to scrape
    """

    utils.log('Starting web-scraping')
    init_tmp_folder(scraper_ids)
    scraper_threads = list()
    for id in scrapers_ids:
        scraper_urls = urls.get(id)
        scraper_thread = threading.Thread(target=scrape_web, args=(ScraperFactory.create_scraper(id), scraper_urls))
        scraper_threads.append(scraper_thread)
        scraper_thread.start()
    
    for scraper_thread in scraper_threads:
        scraper_thread.join()
    
    utils.delete_directory(os.path.join(config.TMP_DIR, config.CHROME_SESSION))
    utils.log('Finished web-scraping')
    utils.log('Joining results...')
    # TODO join results and create final dataset in CSV
    utils.log('... Results joined')
    
if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Will scrape the selected pages. If no pages selected, then it will scrape every page')
    argparser.add_argument('-i', '--idealista', help='launches the idealista scraper', action='store_true')
    argparser.add_argument('-f', '--fotocasa', help='launches the fotocasa scraper', action='store_true')
    argparser.add_argument('--urls-idealista', help='urls to scrape with idealista', required=False, type=str, nargs='+')
    args = argparser.parse_args()

    scraper_ids = list()
    urls = dict()
    if args.idealista: scraper_ids.append(config.IDEALISTA_ID)
    if args.fotocasa: scraper_ids.append(config.FOTOCASA_ID)
    if args.urls_idealista: urls[config.IDEALISTA_ID] = args.urls_idealista

    if not scraper_ids:
        scraper_ids = [config.IDEALISTA_ID, config.FOTOCASA_ID]

    utils.log(f'Scraping {scraper_ids}')
    main(scrapers_ids=scraper_ids, urls=urls)
