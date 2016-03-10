from app import app
from flask import request
import config
import hashlib


@app.route('/weixin', methods=['GET'])
def access_verify():
    if __verification(request.values.get('signature', ''),
                      request.values.get('timestamp', ''), request.values.get('nonce', '')):
        return request.values.get('echostr', "")
    else:
        return 'access verification fail'


def __verification(signature, timestamp, nonce):
    if config.WEIXIN_SKIP_VERIFY:
        return True
    if signature is None or signature == "":
        return False
    return __signature(timestamp, nonce, config.WEIXIN_TOKEN) == signature


def __signature(timestamp, nonce, token):
    tmpstr = ''.join(sorted([token, timestamp, nonce]))
    return hashlib.sha1(tmpstr).hexdigest()
