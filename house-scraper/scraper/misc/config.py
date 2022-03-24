'''
Configuration variables required in multiple files
'''

import os, sys

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0'}

ROOT_DIR = os.path.dirname(os.path.abspath(os.path.join(sys.argv[0], '..')))
TMP_DIR = os.path.join(ROOT_DIR, 'tmp')