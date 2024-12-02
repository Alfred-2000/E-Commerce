import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "e_commerce.settings")
app = Celery("e_commerce")
app.conf.result_expires = 60  # setting ttl to celery task ID (in seconds)
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
from e_commerce.settings import CELERYD_TASK_SOFT_TIME_LIMIT
