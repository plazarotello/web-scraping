import os, shutil
from random import randint
from . import config, proxy_list

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.proxy import Proxy, ProxyType

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

def create_directory(dir_name : str):
    if os.path.exists(dir_name) and os.path.isdir(dir_name):
        shutil.rmtree(dir_name)
    os.mkdir(dir_name)

def create_file(dir : str, file_name : str):
    return open(os.path.join(dir, file_name), 'w+', encoding='UTF8')

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

def reset_user_agent() -> Options:
    options = Options()
    #options.headless = True    
    return options

# https://stackoverflow.com/a/40628176
def proxify():
    available_proxies = proxy_list.get_proxies()
    selected = available_proxies[randint(0, len(available_proxies)-1)]

    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = f'{selected["ip"]}:{selected["port"]}'
    proxy.socks_proxy = f'{selected["ip"]}:{selected["port"]}'
    proxy.ssl_proxy = f'{selected["ip"]}:{selected["port"]}'

    capabilities = webdriver.DesiredCapabilities.FIREFOX
    proxy.add_to_capabilities(capabilities)
    return capabilities

def get_selenium():
    driver_path = os.path.join(config.ROOT_DIR, 'geckodriver.exe')
    
    profile = FirefoxProfile()
    profile.set_preference('general.useragent.override', get_user_agent())
    driver = webdriver.Firefox(executable_path=driver_path, options=reset_user_agent(),
        firefox_profile=profile)
    driver.implicitly_wait(15)
    return driver