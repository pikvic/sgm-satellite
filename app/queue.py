from redis import from_url
from rq import Queue
from rq.job import Job
from uuid import uuid4
from datetime import timedelta
import app.config as config
from app.tasks import clear_files_for_job

red = from_url(config.REDIS_URL)
queue = Queue(connection=red, default_timeout=3600)


def generate_id():
    return str(uuid4())

def create_task(func, params):
    job_id = generate_id()
    params['job_id'] = job_id
    job = queue.enqueue_call(func=func, args=(params,), result_ttl=config.RESULT_TTL, job_id=job_id)
    job_clear_files = queue.enqueue_in(timedelta(seconds=config.RESULT_TTL), func=clear_files_for_job, args=(job_id,), result_ttl=config.RESULT_TTL)
    res = {"job_id": job_id, "url": f"/results/{job_id}"}
    return res

def get_redis():
    return red

def get_queue():
    return queue

def get_jobs_by_ids(queue, job_ids):
    jobs = []
    for job_id in job_ids:
        job = queue.fetch_job(job_id)
        job_dict = {
            'id': job.id, 
            'funcname': job.func_name, 
            'status': job.get_status(),
            'enqueued_at': job.enqueued_at,
            'started_at': job.started_at,
            'ended_at': job.ended_at,
            'result': job.result,
            'args': job.args,
            'kwargs': job.kwargs,
            'error': job.exc_info
        }
        jobs.append(job_dict)
    return jobs

def get_jobs_in_registries():
    q = get_queue()
    jobs_dict = {}
    
    ids_dict = {
        'enqueued': q.get_job_ids(),
        'started': q.started_job_registry.get_job_ids(),
        'finished': q.finished_job_registry.get_job_ids(),
        'failed': q.failed_job_registry.get_job_ids(),
        'scheduled': q.scheduled_job_registry.get_job_ids(),
        'deferred': q.deferred_job_registry.get_job_ids()
    }

    for status, job_ids in ids_dict.items():
        jobs = get_jobs_by_ids(q, job_ids)
        jobs_dict[status] = jobs

    return jobs_dict
