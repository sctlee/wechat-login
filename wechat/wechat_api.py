from app import app
from flask import request, Response
import config
import hashlib
from wechat import get_weixin_qrcode_url


@app.route('/weixin', methods=['GET'])
def access_verify():
    if __verification(request.values.get('signature', ''),
                      request.values.get('timestamp', ''), request.values.get('nonce', '')):
        return request.values.get('echostr', "")
    else:
        return 'access verification fail'


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
