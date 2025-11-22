import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartnote_backend.settings")

app = Celery("smartnote_backend")

# ĐÂY là phần quan trọng – broker trỏ vào Redis
app.conf.broker_url = "redis://127.0.0.1:6379/0"
app.conf.result_backend = "redis://127.0.0.1:6379/0"

app.autodiscover_tasks()
