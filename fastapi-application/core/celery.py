from celery import Celery

from .config import settings


class CeleryConfig:
    broker_url = settings.redis.url
    result_backend = settings.redis.url
    imports = ('core.tasks',)


app = Celery('celery')
app.config_from_object(CeleryConfig)
app.autodiscover_tasks()
