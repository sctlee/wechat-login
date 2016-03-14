import json
from config import WEIXIN_API_URL
import requests
import time
import logging
import random

LOG = logging.getLogger(__name__)

cache_access_token = {
    'value': '',
    'expired_at': time.time()
}

scenes = []


def get_weixin_access_token(app_id, app_secret):
    if time.time() < cache_access_token['expired_at']:
        return cache_access_token['value']

    url = WEIXIN_API_URL + "/cgi-bin/token"
    params = {"grant_type": "client_credential", "appid": app_id, "secret": app_secret}
    headers = {'Accept': 'application/json'}
    r = requests.get(url, params=params, headers=headers)
    r_json = json.loads(r.text)

    cache_access_token['value'] = r_json["access_token"]
    cache_access_token['expired_at'] = time.time() + 3600

    return cache_access_token['value']


def get_weixin_qrcode_url(scene_id, expire_seconds, app_id, app_secret):
    access_token = get_weixin_access_token(app_id, app_secret)
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


def get_weixin_user_info(scene_id, app_id, app_secret):
    access_token = get_weixin_access_token(app_id, app_secret)
    LOG.info('FETCH WEIXIN ACCESS TOKEN %s' % str(access_token))
    filter_scenes = filter(lambda s: s['scene_id'] == scene_id, scenes)
    open_id = filter_scenes and filter_scenes[0]['open_id']
    if open_id:
        user = _get_weixin_user_info(access_token, open_id)
        user['open_id'] = open_id
        return user
    return None


def _get_weixin_user_info(access_token, open_id):
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
