import json
from config import WEIXIN_APP_SECRET, WEIXIN_APP_ID,WEIXIN_API_URL
import requests
import time

access_token = {
    'value': '',
    'expired_at': time.time()
}


def get_weixin_access_token():
    if time.time() < access_token['expired_at']:
        return access_token['value']

    url = WEIXIN_API_URL + "/cgi-bin/token"
    params = {"grant_type": "client_credential", "appid": WEIXIN_APP_ID, "secret": WEIXIN_APP_SECRET}
    headers = {'Accept': 'application/json'}
    r = requests.get(url, params=params, headers=headers)
    r_json = json.loads(r.text)

    access_token['value'] = r_json["access_token"]
    access_token['expired_at'] = time.time() + 3600

    return access_token['value']
