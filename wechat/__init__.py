import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('wechat').setLevel(logging.DEBUG)
logging.getLogger(__name__).info('log init debug')
