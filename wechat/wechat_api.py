from app import app
from flask import request, Response, abort
import config
import hashlib
from wechat import get_weixin_qrcode_url
import time
import xmltodict
import json
import requests


@app.route('/weixin', methods=['GET'])
def access_verify():
    if __verification(request.values.get('signature', ''),
                      request.values.get('timestamp', ''), request.values.get('nonce', '')):
        return request.values.get('echostr', "")
    else:
        return 'access verification fail'


@app.route('/weixin', methods=['POST'])
def access_verify():
    if not __verification(request.values.get('signature', ''),
                      request.values.get('timestamp', ''), request.values.get('nonce', '')):
        abort(401)

    request_xml = xmltodict.parse(request.data)
    request_data = request_xml.get('xml', {})
    event = request_data.get('Event').lower()
    if event not in ('subscribe', 'scan'):
        return __generate_api_response(request_data,"您好！欢迎来到 DaoCloud ！您可以通过微信登录我们的网站：https://www.daocloud.io，点击右下角与我们实时联系。")
    scene_id = request_data.get('EventKey')
    open_id = request_data.get('FromUserName')
    if scene_id and scene_id.startswith('qrscene_'):
        scene_id = scene_id[len('qrscene_'):]

    message = 'hahaha'
    return __generate_api_response(request_data, message)


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


@app.route('/get_qrcode')
def get_qrcode():
    url = get_weixin_qrcode_url('hello', 604800)
    return Response(url)


def __verification(signature, timestamp, nonce):
    if config.WEIXIN_SKIP_VERIFY:
        return True
    if signature is None or signature == "":
        return False
    return __signature(timestamp, nonce, config.WEIXIN_TOKEN) == signature


def __signature(timestamp, nonce, token):
    tmpstr = ''.join(sorted([token, timestamp, nonce]))
    return hashlib.sha1(tmpstr).hexdigest()
