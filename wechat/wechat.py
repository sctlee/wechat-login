import json
from config import WEIXIN_APP_SECRET, WEIXIN_APP_ID, WEIXIN_API_URL
import requests
import time
import logging
import random

LOG = logging.getLogger(__name__)

access_token = {
    'value': '',
    'expired_at': time.time()
}

scenes = []


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


def get_weixin_qrcode_url(scene_id, expire_seconds):
    access_token = get_weixin_access_token()
    LOG.info('FETCH WEIXIN ACCESS TOKEN %s scene_id %s' % (str(access_token), scene_id))
    ticket = get_weixin_qrcode_ticket(access_token, scene_id, expire_seconds)
    return "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=" + ticket


def get_weixin_qrcode_ticket(access_token, scene_id, expire_seconds):
    url = "https://api.weixin.qq.com/cgi-bin/qrcode/create"
    params = {"access_token": access_token}
    data = {"expire_seconds": expire_seconds, "action_name": "QR_SCENE",
            "action_info": {"scene": {"scene_id": scene_id}}}
    headers = {'Accept': 'application/json'}
    r = requests.post(url, params=params, headers=headers, data=json.dumps(data))
    r_json = json.loads(r.text)
    return r_json['ticket']


def get_weixin_user_info(access_token, open_id):
    url = "https://api.weixin.qq.com/cgi-bin/user/info"
    params = {"access_token": access_token, "openid": open_id, "lang": "zh_CN"}
    headers = {'Accept': 'application/json'}
    r = requests.get(url, params=params, headers=headers)
    return json.loads(r.text)


def get_weixin_scene_id():
    scene_id = __generate_scene_id()
    scenes.append({
        'scene_id': str(scene_id),
        'open_id': ''
    })
    return scene_id


def bind_weixin(scene_id, open_id):
    filter_scenes = filter(lambda s: s['scene_id'] == scene_id, scenes)
    scene = filter_scenes and filter_scenes[0]
    if scene:
        scene['open_id'] = open_id
        return True
    else:
        return False


def __generate_scene_id():
    return len(scenes) * 10000000 + random.randrange(1, 1000000, 1)
