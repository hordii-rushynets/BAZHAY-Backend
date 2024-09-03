from django.db import models
from django.utils import timezone

from datetime import timedelta

from user.models import BazhayUser


class Premium(models.Model):
    bazhay_user = models.OneToOneField(BazhayUser, on_delete=models.CASCADE, related_name='premium')
    date_of_payment = models.DateTimeField(default=timezone.now)
    is_used_trial = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.bazhay_user.email} to {self.date_of_payment}"

    @property
    def is_active(self):
        """The subscription is active if the payment date is not older than one month"""
        return timezone.now() <= self.date_of_payment + timedelta(days=30)


