import asyncio
from typing import Dict
from datetime import datetime

class JobQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.active_jobs: Dict[str, Dict] = {}  # track jobs by id

    async def worker(self):
        while True:
            job = await self.queue.get()
            job_id = job["id"]
            self.active_jobs[job_id]["status"] = "running"
            try:
                await job["func"](*job["args"], **job["kwargs"])
                self.active_jobs[job_id]["status"] = "done"
            except Exception as e:
                self.active_jobs[job_id]["status"] = "failed"
                self.active_jobs[job_id]["error"] = str(e)
            finally:
                self.queue.task_done()

    def add_job(self, func, *args, **kwargs):
        job_id = str(datetime.utcnow().timestamp()).replace(".", "")
        job_data = {
            "id": job_id,
            "func": func,
            "args": args,
            "kwargs": kwargs,
            "status": "queued",
            "created_at": datetime.utcnow()
        }
        self.active_jobs[job_id] = job_data
        self.queue.put_nowait(job_data)
        return job_data

    def list_jobs(self):
        return list(self.active_jobs.values())

# singleton queue
job_queue = JobQueue()
