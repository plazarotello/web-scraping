import requests
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem


# https://medium.com/analytics-vidhya/the-art-of-not-getting-blocked-how-i-used-selenium-python-to-scrape-facebook-and-tiktok-fd6b31dbe85f
def get_user_agent():
    """
    Generates a random user agent
    """
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

# ---------------------------------------------------------

PROXIES = 'https://hidemy.name/es/proxy-list/?maxtime=1000&type=hs&anon=4'

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
            r_headers = {'User-Agent': get_user_agent()}
            r = requests.get(PROXIES, headers=r_headers)
            r.raise_for_status()    # if returned code is unsuccesful, raise error
            html = r.content
        except (requests.HTTPError, requests.ConnectionError) as e:
            print(f'Error trying to get proxies {PROXIES}: {e}')

        # if there are no errors opening the URL, returns the soup
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.body.select('div.wrap > div.services_proxylist.services > div.inner > div.table_block > table > tbody')[0]
        for proxy in table.find_all('tr'):
            features = proxy.find_all('td')
            __proxy_list.append({'ip': features[0].getText(), 'port': features[1].getText()})
    return __proxy_list