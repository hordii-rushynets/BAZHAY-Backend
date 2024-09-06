from celery import shared_task
from django.conf import settings
from .services import CurrencyRatesService
from celery.signals import worker_ready
import redis

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    ssl=settings.REDIS_USE_SSL
)

@worker_ready.connect
def at_startup(**kwargs):
    update_currency_rates.delay()


@shared_task
def update_currency_rates():
    service = CurrencyRatesService()
    currency = ['UAH', 'USD', 'EUR', 'PLN', 'GBP', 'CAD', 'NOK', 'CHF', 'SEK', ]
    rates = {}

    for currency in currency:
        rates[currency] = service.get_currency_to_uah(currency)
    redis_client.set('currency_rates', str(rates), ex=86400)

