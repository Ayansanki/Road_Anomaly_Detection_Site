import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'road_anomaly_detection.settings')

app = Celery('road_anomaly_detection')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()