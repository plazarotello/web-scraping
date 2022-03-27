'''
Configuration variables required in multiple files
'''

import os, sys

# ---------------------------------------------------------

IDEALISTA_ID = 'idealista'
IDEALISTA_URL = 'https://www.idealista.com'

FOTOCASA_ID = 'fotocasa'

PISOSCOM_ID = 'pisos.com'

KASAZ_ID = 'kasaz'

# ---------------------------------------------------------

ROOT_DIR = os.path.dirname(os.path.abspath(os.path.join(sys.argv[0], '..')))
TMP_DIR = os.path.join(ROOT_DIR, 'tmp')
CHROME_SESSION = 'chrome-session'

# ---------------------------------------------------------

RANDOM_MIN_WAIT = 30.2
RANDOM_MAX_WAIT = 56.7

RANDOM_SMALL_MIN_WAIT = 5.0
RANDOM_SMALL_MAX_WAIT = 15.0