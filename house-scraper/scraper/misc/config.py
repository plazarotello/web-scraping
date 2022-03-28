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

# ---------------------------------------------------------

IDEALISTA_ID = 'idealista'
IDEALISTA_URL = 'https://www.idealista.com'
IDEALISTA_FILE = os.path.join(DATASET_DIR, IDEALISTA_ID + '.csv')

FOTOCASA_ID = 'fotocasa'

PISOSCOM_ID = 'pisos.com'

KASAZ_ID = 'kasaz'

# ---------------------------------------------------------

RANDOM_MIN_WAIT = 20
RANDOM_MAX_WAIT = 40

RANDOM_SMALL_MIN_WAIT = 10
RANDOM_SMALL_MAX_WAIT = 30

MAX_WORKERS = 6
