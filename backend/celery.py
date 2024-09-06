import os

import celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = celery.Celery('backend')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'update-currency-rates-every-day': {
        'task': 'ability.update_currency_rates',
        'schedule': crontab(hour=0, minute=0),
    },
}

app.conf.timezone = 'UTC'
app.conf.broker_connection_retry_on_startup = True