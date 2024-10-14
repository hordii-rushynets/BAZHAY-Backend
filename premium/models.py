import datetime

from django.db import models
from django.utils import timezone

from datetime import timedelta

from user.models import BazhayUser


class Premium(models.Model):
    bazhay_user = models.OneToOneField(BazhayUser, on_delete=models.CASCADE, related_name='premium')
    date_of_payment = models.DateTimeField(default=timezone.now)
    is_used_trial = models.BooleanField(default=True)
    is_an_annual_payment = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.bazhay_user.email} to {self.date_of_payment}"

    @property
    def is_active(self):
        """The subscription is active"""
        if self.is_an_annual_payment:
            period = timezone.now() <= (self.date_of_payment + timedelta(days=365))
            if period is False:
                self.is_an_annual_payment = False
            return period
        elif self.is_used_trial:
            return timezone.now() <= (self.date_of_payment + timedelta(days=7))
        else:
            return timezone.now() <= (self.date_of_payment + timedelta(days=30))

    @property
    def expiration_date(self):
        if self.is_an_annual_payment:
            return self.date_of_payment + timedelta(days=365)

        return self.date_of_payment + timedelta(days=30)

