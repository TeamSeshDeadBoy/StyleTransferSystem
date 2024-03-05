from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from redis import Redis
from rq import Queue
from utils.result_by_id import get_job_result
from utils.status_by_id import get_job_status
from worker import picture, picture_prod
from dotenv.main import load_dotenv
import os


### LOADING ENVIRONMENTAL VARIABLES
load_dotenv()
redis_host = os.environ["REDIS_HOST"]
redis_port = os.environ["REDIS_PORT"]
mode = os.environ["MODE"]
ip_adress = os.environ["BACKEND_ADRESS_IP"]
port = os.environ["BACKEND_ADRESS_PORT"]


### REDIS & FASTAPI INITIALIZATIONS
q = Queue(connection=Redis(host=redis_host, port=int(redis_port)))
app = FastAPI()


### HELLO WORLD TESTER
@app.get("/")
async def root():
    return {"message": "Hello World"}


### BaseModel CLASS OF BODY FOR POST ENDPOINT /add_job/picture
class Item(BaseModel):
    foldername: str
    idx_person: int
    prompt: str | None = None
    num_images_user: int | None = 1
    num_steps_user: int | None = 50
    style_strength_user: int | None = 20


### ENDPOINT FOR GPU: VOLUME PRODUCTION \ NO VOLUME TESTING
@app.post("/add_job/picture/")
async def add_job_calculate(item: Item):
    if mode == "DEV":
        job = q.enqueue(picture, item.foldername)
    if mode == "PROD":
        job = q.enqueue(picture_prod, item.foldername, item.idx_person, item.prompt, item.num_images_user, item.num_steps_user, item.style_strength_user)
    return {"job_id": job.get_id(), "filename": item.foldername}


### ENDPOINT FOR GETTING RQ JOB STATUS BY JOB_ID
@app.get("/job_status/{idd}")
async def job_status(idd):
    status = get_job_status(idd)
    return {"job_status": status}


### ENDPOINT FOR GETTING RQ JOB RESULT BY JOB_ID
@app.get("/job_result/{idd}")
async def job_result(idd):
    status = get_job_result(idd)
    return {"job_result": status}


### ENDPOINT FOR GETTING ALL ENQUEUED JOBS (default queue of RQ)
@app.get("/jobs/queued")
async def jobs():
    return {"jobs": q.jobs}


### ENDPOINT OF GETTING ALL FINISHED JOB_IDS (default queue of RQ)
@app.get("/jobs/finished")
async def jobs():
    return {"jobs": q.finished_job_registry.get_job_ids()}


### ENDPOINT OF GETTING ALL FAILED JOB_IDS (default queue of RQ)
@app.get("/jobs/failed")
async def jobs():
    return {"jobs": q.failed_job_registry.get_job_ids()}


### SETTING UP FASTAPI SERVER
if __name__ == "__main__":
    uvicorn.run(app, host=ip_adress, port=int(port))
