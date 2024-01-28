from fastapi import FastAPI
import uvicorn

from redis import Redis
from rq import Queue

from utils.result_by_id import get_job_result
from utils.status_by_id import get_job_status
from worker import calculator, picture

q = Queue(connection=Redis())

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/add_job/calculate/{xy}")
async def add_job_calculate(xy):
    x, y = [int(i) for i in xy.split('_')]
    job = q.enqueue(calculator, x, y)
    return {"job_id": job.get_id(), "x": x, "y": y}


@app.get("/add_job/picture/{filename}")
async def add_job_calculate(filename):
    job = q.enqueue(picture, filename)
    return {"job_id": job.get_id(), "filename": filename}


@app.get("/job_status/{idd}")
async def job_status(idd):
    status = get_job_status(idd)
    return {"job_status": status}


@app.get("/job_result/{idd}")
async def job_result(idd):
    status = get_job_result(idd)
    return {"job_result": status}


@app.get("/jobs/queued")
async def jobs():
    return {"jobs": q.jobs}


@app.get("/jobs/finished")
async def jobs():
    return {"jobs": q.finished_job_registry.get_job_ids()}


@app.get("/jobs/failed")
async def jobs():
    return {"jobs": q.failed_job_registry.get_job_ids()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
