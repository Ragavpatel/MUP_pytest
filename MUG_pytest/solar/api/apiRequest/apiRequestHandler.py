import requests
from solar.api.apiHelper import apiConfig
import logging
from solar.api.apiHelper import apiCalls
from solar.config import solar_config

def get_token():
    url = f"{apiConfig.authorisation_URL}"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }
    payload = 'scope=DomesticApi&grant_type=client_credentials&client_id=76cee353-b5bd-4872-9371-f8e0e58b6207&client_secret=Au0tOm@at1on'
    logging.info(f"POST {url}")
    response = requests.post(url, headers=headers, data=payload, timeout=apiConfig.TIMEOUT)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        logging.debug(f'Token is : {token} ')
        return token
    else:
        logging.error("Failed to fetch token:", response.text)
        return None
    
def get_data_from_quoteid(quoteId, token):
    url = apiConfig.solar_result_URL
    headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer '+token
    }
    return apiCalls.get(url, endpoint=quoteId, headers=headers)



    