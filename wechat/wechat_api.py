# coding=utf8
from __future__ import unicode_literals
from app import app
from flask import request, Response, abort
import config
import hashlib
from wechat import get_weixin_qrcode_url, get_weixin_scene_id, bind_weixin, get_weixin_user_info
import time
import xmltodict
import json
import requests
import logging
from functools import wraps


LOG = logging.getLogger(__name__)


@app.route('/weixin', methods=['GET'])
def access_verify():
    if __verification(request.values.get('signature', ''),
                      request.values.get('timestamp', ''), request.values.get('nonce', '')):
        LOG.debug('echostr: %s' % request.values.get('echostr', ""))
        return request.values.get('echostr', "")
    else:
        LOG.debug('weixin error')
        return 'access verification fail'


@app.route('/weixin', methods=['POST'])
def send_msg():
    if not __verification(request.values.get('signature', ''),
                      request.values.get('timestamp', ''), request.values.get('nonce', '')):
        abort(401)

    request_xml = xmltodict.parse(request.data)
    request_data = request_xml.get('xml', {})
    event = request_data.get('Event').lower()
    if event not in ('subscribe', 'scan'):
        return __generate_api_response(request_data, '操作不符合要求')
    scene_id = request_data.get('EventKey')
    open_id = request_data.get('FromUserName')
    if scene_id and scene_id.startswith('qrscene_'):
        scene_id = scene_id[len('qrscene_'):]

    if not bind_weixin(scene_id, open_id):
        return __generate_api_response(request_data, '登录失败')

    return __generate_api_response(request_data, '欢迎登录东风系统')


def __generate_response(open_id, message):
    url = config.WEIXIN_API_URL + "/cgi-bin/message/custom/send"
    params = {}
    data = {"touser": open_id, "msgtype": "text", "text": {"content": message}}
    headers = {'Accept': 'application/json', "Content-Type": "application/json; charset=utf-8"}
    requests.post(url, params=params, headers=headers, data=json.dumps(data, ensure_ascii=False).encode("utf-8"))


def __generate_api_response(request_data, message):
    response = u"""
    <xml>
    <ToUserName><![CDATA[{to}]]></ToUserName>
    <FromUserName><![CDATA[{from}]]></FromUserName>
    <CreateTime>{now}</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[{message}]]></Content>
    </xml>
    """
    response_value = {
        'now': int(time.time()),
        'from': request_data.get("ToUserName"),
        'to': request_data.get("FromUserName"),
        'message': message
    }
    return response.format(**response_value)


def requires_app_auth(func):
    @wraps(func)
    def inner(*args, **kwargs):
        app_id = request.headers.get('WEIXIN_APP_ID')
        app_secret = request.headers.get('WEIXIN_APP_SECRET')
        if app_id and app_secret:
            return func(app_id, app_secret, *args, **kwargs)
        abort(401)

    return inner


@app.route('/get_qrcode')
@requires_app_auth
def get_qrcode(app_id, app_secret):
    LOG.debug('get scene_id')
    scene_id = get_weixin_scene_id()
    LOG.debug('scene_id: %s' % scene_id)
    url = get_weixin_qrcode_url(scene_id, 604800, app_id, app_secret)
    LOG.debug('url: %s' % url)
    return Response(json.dumps({'url': url, 'scene_id': scene_id}), mimetype='application/json')


@app.route('/get_status/<scene_id>')
@requires_app_auth
def check_login_status(app_id, app_secret, scene_id):
    timeout = int(request.values.get('timeout'))
    while timeout:
        user = get_weixin_user_info(scene_id, app_id, app_secret)
        if user:
            return Response(json.dumps({'username': user['nickname'], 'open_id': user['open_id']}), mimetype='application/json')
        time.sleep(1)
        timeout -= 1
    abort(404)
    # return Response(json.dumps({'name': user['name'], 'open_id': user['open_id']}), mimetype='application/json')


def __verification(signature, timestamp, nonce):
    if config.WEIXIN_SKIP_VERIFY:
        return True
    if signature is None or signature == "":
        return False
    return __signature(timestamp, nonce, config.WEIXIN_TOKEN) == signature


def __signature(timestamp, nonce, token):
    tmpstr = ''.join(sorted([token, timestamp, nonce]))
    return hashlib.sha1(tmpstr).hexdigest()
