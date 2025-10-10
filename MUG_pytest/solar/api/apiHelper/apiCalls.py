import requests
from solar.api.apiHelper import apiConfig
import logging


def get(url, endpoint=None, headers=None, params=None):
    url = f"{url}{endpoint}"
    logging.info(f"GET {url}")
    return requests.get(url, headers=headers, params=params, timeout=apiConfig.TIMEOUT)

def post(url, endpoint= None, headers=None, payload=None):
    url = f"{url}{endpoint}"
    logging.info(f"POST {url}")
    return requests.post(url, headers=headers, json=payload, timeout=apiConfig.TIMEOUT)