from redis import Redis
from rq import Queue, Worker

redis = Redis()
queue = Queue('default')

worker = Worker([queue], connection=redis)
worker.work()
