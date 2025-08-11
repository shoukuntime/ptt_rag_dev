from celery import Celery
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ptt_rag_dev.settings')
django.setup()

app = Celery("ptt_rag_dev", broker="redis://redis:6379/0", backend="redis://redis:6379/0")
app.autodiscover_tasks()