import logging
import os
import time
import traceback
from functools import wraps

filename = time.strftime("%Y-%m-%d", time.localtime(time.time()))
logger = logging.getLogger('test')
logger.setLevel(level=logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
try:
    if not os.path.exists('./app/log/logs'):
        os.mkdir('./app/log/logs')
    file_handler = logging.FileHandler(f'./app/log/logs/{filename}-log.log')
except:
    file_handler = logging.FileHandler(f'{filename}-log.log')

file_handler.setLevel(level=logging.INFO)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def log(func):
    @wraps(func)
    def log_(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"\n{func.__qualname__} is error,params:{(args, kwargs)},here are details:\n{traceback.format_exc()}")

    return log_
