import os, shutil, uuid
from random import randint, uniform
from time import sleep
from . import config, proxy_list

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

def create_directory(dir_name : str):
    if os.path.exists(dir_name) and os.path.isdir(dir_name):
        shutil.rmtree(dir_name)
    os.mkdir(dir_name)

def create_file(dir : str, file_name : str):
    return open(os.path.join(dir, file_name), 'w+', encoding='UTF8')

def duplicate_folder(dir : str, dest : str):
    shutil.copytree(dir, dest)

# https://medium.com/analytics-vidhya/the-art-of-not-getting-blocked-how-i-used-selenium-python-to-scrape-facebook-and-tiktok-fd6b31dbe85f
def get_user_agent():
    sw_names = [SoftwareName.FIREFOX.value, SoftwareName.BRAVE.value,
        SoftwareName.CHROME.value, SoftwareName.CHROMIUM.value,
        SoftwareName.EDGE.value, SoftwareName.OPERA.value,
        SoftwareName.SAFARI.value]
    os_names = [OperatingSystem.LINUX.value, 
        OperatingSystem.MAC_OS_X.value, 
        OperatingSystem.WINDOWS.value]
    user_agent_rotator = UserAgent(software_names=sw_names, operating_systems=os_names, 
        limit=100)
    return user_agent_rotator.get_random_user_agent()

def set_human_options() -> Options:
    options = webdriver.ChromeOptions()

    og_session = os.path.join(config.ROOT_DIR, 'chrome-session')
    dup_session = os.path.join(config.TMP_DIR, 'chrome-session', str(uuid.uuid4()))
    duplicate_folder(og_session, dup_session)

    options.add_argument(f'user-data-dir={dup_session}')
    options.add_argument('no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=800,600')
    options.add_argument('--headless')
    return options

# https://stackoverflow.com/a/40628176
def proxify():
    available_proxies = proxy_list.get_proxies()
    selected = available_proxies[randint(0, len(available_proxies)-1)]
    
    capabilities = webdriver.DesiredCapabilities.FIREFOX
    capabilities['marionette'] = True
    capabilities['proxy'] = {
        'proxyType': 'MANUAL',
        'httpProxy': f'{selected["ip"]}:{selected["port"]}',
        'ftpProxy': f'{selected["ip"]}:{selected["port"]}',
        'sslProxy': f'{selected["ip"]}:{selected["port"]}'
    }
    return capabilities

def get_selenium():
    driver_path = os.path.join(config.ROOT_DIR, 'chromedriver.exe')
    driver = webdriver.Chrome(executable_path=driver_path, options=set_human_options())
    driver.implicitly_wait(15)
    return driver

def wait():
    sleep(uniform(config.RANDOM_MIN_WAIT, config.RANDOM_MAX_WAIT))

def mini_wait():
    sleep(uniform(config.RANDOM_SMALL_MIN_WAIT, config.RANDOM_SMALL_MAX_WAIT))