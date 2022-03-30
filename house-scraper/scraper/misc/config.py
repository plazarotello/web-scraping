'''
Configuration variables required in multiple files
'''

import os
import sys

# ---------------------------------------------------------

ROOT_DIR = os.path.dirname(os.path.abspath(os.path.join(sys.argv[0], '..')))
TMP_DIR = os.path.join(ROOT_DIR, 'tmp')
DATASET_DIR = os.path.join(ROOT_DIR, 'dataset')
CHROME_SESSION = 'chrome-session'
BUSTER = os.path.join(ROOT_DIR, 'buster_1.3.crx')

# ---------------------------------------------------------

IDEALISTA_ID = 'idealista'
IDEALISTA_URL = 'https://www.idealista.com'
IDEALISTA_FILE = os.path.join(DATASET_DIR, IDEALISTA_ID + '.csv')
IDEALISTA_MAPS = os.path.join(DATASET_DIR, IDEALISTA_ID + '-maps')

FOTOCASA_ID = 'fotocasa'
FOTOCASA_URL = 'https://www.fotocasa.es/es/'
FOTOCASA_FILE = os.path.join(DATASET_DIR, FOTOCASA_ID + '.csv')

PISOSCOM_ID = 'pisos.com'

KASAZ_ID = 'kasaz'

# ---------------------------------------------------------

RANDOM_MIN_WAIT = 10
RANDOM_MAX_WAIT = 30

RANDOM_SMALL_MIN_WAIT = 10
RANDOM_SMALL_MAX_WAIT = 20

CHANCE_MEGA_WAIT = 0.2
MEGA_MIN_WAIT = 60
MEGA_MAX_WAIT = 240

MAX_WORKERS = 3
