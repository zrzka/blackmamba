#!python3

import requests
import traceback
from blackmamba.log import error


try:
    exec(requests.get('http://bit.ly/get-blackmamba').text)

except Exception:
    error('Failed to fetch & execute installer')
    error(traceback.format_exc())
