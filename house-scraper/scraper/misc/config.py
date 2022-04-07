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
IDEALISTA_FILE = os.path.join(
    DATASET_DIR, IDEALISTA_ID + '.csv')   # Directory to save data
# Directory to save downloaded images
IDEALISTA_MAPS = os.path.join(DATASET_DIR, IDEALISTA_ID + '-maps')
# Directory to save temporary files
IDEALISTA_TMP = os.path.join(TMP_DIR, IDEALISTA_ID)

FOTOCASA_ID = 'fotocasa'
FOTOCASA_URL = 'https://www.fotocasa.es/es/'
# Directory to save downloaded images
FOTOCASA_IMG_DIR = os.path.join(DATASET_DIR, FOTOCASA_ID+'-imgs')
# Directory to save data
FOTOCASA_FILE = os.path.join(DATASET_DIR, FOTOCASA_ID + '.csv')
# number of iteractions for scrolling in location pages
FOTOCASA_SCROLL_LOCATION_PAGE = 20
# number of iteractions for scrolling in house pages
FOTOCASA_SCROLL_HOUSE_PAGE = 3
# number of pages to process
FOTOCASA_NUM_PAGES_TO_READ = 100

# name of merged dataframe
MERGED_FILE = os.path.join(DATASET_DIR, 'fotocasa_idealista_merged.csv')
# name of zip merged dataframe
MERGED_ZIP_FILE = os.path.join(
    DATASET_DIR, 'fotocasa_idealista-villaverde_salamanca-2022_04.zip')

# ---------------------------------------------------------

SCROLL_WAIT = 0.5

RANDOM_MIN_WAIT = 10
RANDOM_MAX_WAIT = 30

RANDOM_SMALL_MIN_WAIT = 7.5
RANDOM_SMALL_MAX_WAIT = 15

CHANCE_MEGA_WAIT = 0.2
MEGA_MIN_WAIT = 60
MEGA_MAX_WAIT = 80

SYNCHRO_MAX_WAIT = 90

MAX_WORKERS = 6
