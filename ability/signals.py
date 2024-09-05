from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Wish
from .services import CurrencyRatesService


@receiver(pre_save, sender=Wish)
def update_price_in_uah(sender, instance, **kwargs):
    if instance.price and instance.currency:
        currency_service = CurrencyRatesService()
        rate = currency_service.get_currency_to_uah(instance.currency)
        instance.price_in_uah = instance.price * rate
    else:
        instance.price_in_uah = None
