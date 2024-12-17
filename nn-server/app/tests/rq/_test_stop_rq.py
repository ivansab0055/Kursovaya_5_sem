import argparse

from redis import Redis
from rq import Queue
from rq.command import send_stop_job_command

try:
    from tests.rq._task import example
except ModuleNotFoundError:
    from _task import example
import time

"""
sudo service redis-server start
rq worker

python3 _test_stop_rq.py --wait=190 --seconds=190
"""

parser = argparse.ArgumentParser(description='Videos to images')
parser.add_argument('-w', '--wait', type=int, default=2, help='Timeout to sleep')
parser.add_argument('-s', '--seconds', type=int, default=15, help='Job seconds to print')
args = parser.parse_args()

# Идентификатор задачи
redis_conn = Redis()
q = Queue(connection=redis_conn)  # отсутствие аргументов подразумевает наличие очереди по умолчанию

job = q.enqueue(example, seconds=args.seconds, job_timeout=-1)
print(job.return_value())

time.sleep(args.wait)
send_stop_job_command(redis_conn, job.get_id())
print('Stop')

# Теперь подождите некоторое время, пока рабочий не закончит
time.sleep(1)
print(job.return_value())
