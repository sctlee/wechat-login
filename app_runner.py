from app import app
from wechat import wechat_api
from gevent import monkey

monkey.patch_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5200, debug=True)
