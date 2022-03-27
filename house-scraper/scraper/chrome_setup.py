import os
from time import sleep
from misc import utils, config

if __name__=='__main__':
    utils.delete_directory(os.path.join(config.ROOT_DIR, config.CHROME_SESSION))

    with utils.get_selenium() as driver:
        driver.get(config.IDEALISTA_URL)
        sleep(60)