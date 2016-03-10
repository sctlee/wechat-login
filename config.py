import os


def clean_url(base_url):
    if not base_url:
        return
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    return base_url

WEIXIN_SKIP_VERIFY = os.getenv('WEIXIN_SKIP_VERIFY', False)
WEIXIN_TOKEN = os.getenv('WEIXIN_TOKEN', 'hahahehe')
WEIXIN_APP_ID = os.getenv('WEIXIN_APP_ID')
WEIXIN_APP_SECRET = os.getenv('WEIXIN_APP_SECRET')
WEIXIN_API_URL = clean_url(os.getenv("WEIXIN_API_URL", "https://api.weixin.qq.com"))
