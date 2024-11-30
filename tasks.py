from celery import Celery
from main import process_video

celery_app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

@celery_app.task
def process_video_task(url):
    return process_video(url)
