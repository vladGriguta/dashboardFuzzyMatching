import os

import redis
from rq import Worker, Queue, Connection

if os.path.exists('matched_data.csv'): os.remove('matched_data.csv')

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()