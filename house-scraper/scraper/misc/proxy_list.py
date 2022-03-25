from . import config
import requests
import re
from bs4 import BeautifulSoup

PROXIES = 'https://free-proxy-list.net/'

__proxy_list = list()

def get_proxies() -> list:
    """
    Returns
    -------
    A cached list of proxies
    """
    global __proxy_list
    if not __proxy_list:
        __proxy_list = list()
        try:
            r = requests.get(PROXIES, headers=config.HEADERS)
            r.raise_for_status()    # if returned code is unsuccesful, raise error
            html = r.content
        except (requests.HTTPError, requests.ConnectionError) as e:
            print(f'Error trying to get proxies {PROXIES}: {e}')

        # if there are no errors opening the URL, returns the soup
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('section', {'id' : 'list'}).select('div.container > div.table-responsive > div > table > tbody')[0]
        for proxy in table.find_all('tr'):
            features = proxy.find_all('td')
            if features[6].getText() == 'yes':
                __proxy_list.append({'ip': features[0].getText(), 'port': features[1].getText()})
    return __proxy_list