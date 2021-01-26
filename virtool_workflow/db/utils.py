from virtool_workflow.data_model import Job


def convert_job_to_job_document(job: Job):
    return {
        "_id": job._id,
        "args": job.args,
        "mem": job.mem,
        "proc": job.proc,
        "task": job.task,
        "status": job.status,
    }
