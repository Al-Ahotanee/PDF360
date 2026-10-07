import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job, JobStatus, JobType


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, owner_id: uuid.UUID, job_type: JobType, input_params: dict) -> Job:
        job = Job(owner_id=owner_id, job_type=job_type, status=JobStatus.QUEUED, input_params=input_params)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_by_id(self, job_id: uuid.UUID) -> Job | None:
        return self.db.execute(select(Job).where(Job.id == job_id)).scalar_one_or_none()

    def mark_processing(self, job: Job, celery_task_id: str | None = None) -> Job:
        job.status = JobStatus.PROCESSING
        if celery_task_id:
            job.celery_task_id = celery_task_id
        self.db.commit()
        self.db.refresh(job)
        return job

    def mark_done(self, job: Job, result: dict) -> Job:
        job.status = JobStatus.DONE
        job.result = result
        self.db.commit()
        self.db.refresh(job)
        return job

    def mark_failed(self, job: Job, error_message: str) -> Job:
        job.status = JobStatus.FAILED
        job.error_message = error_message
        self.db.commit()
        self.db.refresh(job)
        return job
