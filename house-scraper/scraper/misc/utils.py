import os, shutil
from . import config
from selenium import webdriver

def create_directory(dir_name : str):
    if os.path.exists(dir_name) and os.path.isdir(dir_name):
        shutil.rmtree(dir_name)
    os.mkdir(dir_name)

def create_file(dir : str, file_name : str):
    return open(os.path.join(dir, file_name), 'w+')

def get_selenium():
    options = webdriver.FirefoxOptions()
    options.headless = True
    options.add_argument(f'user-agent={config.HEADERS["User-Agent"]}')
    
    driver_path = os.path.join(config.ROOT_DIR, 'geckodriver.exe')
    
    driver = webdriver.Firefox(executable_path=driver_path, options=options)
    driver.implicitly_wait(5)
    return driver