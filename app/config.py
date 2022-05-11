import os
from pathlib import Path

ROOT =  Path()
#UPLOAD_DIR = ROOT / 'static' / 'upload'
DOWNLOAD_DIR = ROOT / 'static' / 'download'
RESULT_TTL = 600
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
USER = os.getenv('USER', 'qwerty')
PASSWORD = os.getenv('PASSWORD', 'qwerty')
AUTH = (USER, PASSWORD)
URL_DSYSTEM = 'https://dsystem.satellite.dvo.ru:4004/dsystem'
URL_NOAA_A0 = 'https://davrods.satellite.dvo.ru/data/NOAA'
URL_NOAA_RESULT = 'https://davrods.satellite.dvo.ru/process/result/term.proj.irods'
