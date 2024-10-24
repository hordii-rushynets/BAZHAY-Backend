import datetime

from django.db import models
from django.utils import timezone

from datetime import timedelta

from user.models import BazhayUser


class Premium(models.Model):
    bazhay_user = models.OneToOneField(BazhayUser, on_delete=models.CASCADE, related_name='premium')
    end_date = models.DateTimeField(null=True, blank=True)
    is_an_annual_payment = models.BooleanField(default=False)
    is_trial_period = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.bazhay_user.email} to {self.end_date}"

    @property
    def is_active(self):
        """The subscription is active"""
        return True if timezone.now() < self.end_date else False


