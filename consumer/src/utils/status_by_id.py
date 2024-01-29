from redis import Redis
from rq.job import Job
from dotenv.main import load_dotenv
import os
load_dotenv()


redis_host = os.environ["REDIS_HOST"]
redis_port = os.environ["REDIS_PORT"]


def get_job_status(idd):
    job = Job.fetch(idd, connection=Redis(host=redis_host, port=int(redis_port)))
    return(job.get_status())