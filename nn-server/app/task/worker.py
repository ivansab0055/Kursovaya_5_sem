import sys

import redis
from rq import Worker

# Preload libraries
try:
    from .preload_libs import *
except ImportError:
    from preload_libs import *

console_logger.info('Worker libs preload')

queue_name = sys.argv[2] or ['default']
redis_url = sys.argv[4]
console_logger.debug(f'qs: {queue_name}, redis_url: {redis_url}')

redis_url = redis_url
redis_connection = redis.from_url(redis_url)

worker = Worker([queue_name], connection=redis_connection)
worker.work()
