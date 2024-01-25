from redis import Redis
from rq.job import Job


def get_job_result(idd):
    redis = Redis()
    job = Job.fetch(idd, connection=redis)
    return(job.result)