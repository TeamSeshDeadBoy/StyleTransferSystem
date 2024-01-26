from redis import Redis
from rq.command import send_shutdown_command
from rq.worker import Worker

redis = Redis()

workers = Worker.all(redis)
workers_num = Worker.count(connection=redis)
print("Killed: ", workers_num)
for worker in workers:
   send_shutdown_command(redis, worker.name)