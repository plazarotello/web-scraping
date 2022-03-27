'''
Configuration variables required in multiple files
'''

import os, sys

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0'}

IDEALISTA_URL = 'https://www.idealista.com'
IDEALISTA_COOKIE = 'idealista_cookie.pkl'

ROOT_DIR = os.path.dirname(os.path.abspath(os.path.join(sys.argv[0], '..')))
TMP_DIR = os.path.join(ROOT_DIR, 'tmp')

RANDOM_MIN_WAIT = 30.2
RANDOM_MAX_WAIT = 56.7

RANDOM_SMALL_MIN_WAIT = 5.0
RANDOM_SMALL_MAX_WAIT = 15.0