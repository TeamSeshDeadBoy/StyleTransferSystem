from redis import Redis
from rq.command import send_shutdown_command
from rq.worker import Worker

from dotenv.main import load_dotenv
import os
load_dotenv()


redis_host = os.environ["REDIS_HOST"]
redis_port = os.environ["REDIS_PORT"]
redis = Redis(host=redis_host, port=int(redis_port))

workers = Worker.all(redis)
workers_num = Worker.count(connection=redis)
print("Killed: ", workers_num)
for worker in workers:
   send_shutdown_command(redis, worker.name)