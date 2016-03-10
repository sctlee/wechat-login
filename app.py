from flask import Flask, Response, request

import wechat.wechat_api

app = Flask(__name__)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5200)
