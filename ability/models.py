from django.db import models
from django.core.exceptions import ValidationError

import ability.choices as choices

from user.models import BazhayUser


def validate_media(value):
    if not value:
        return

    content_type = getattr(value, 'content_type', None)
    if content_type and not content_type.startswith(('image/', 'video/')):
        raise ValidationError('Only images and videos are allowed.')


class Wish(models.Model):
    ACCESS_TYPE_CHOICES = choices.access_type_choices
    CURRENCY_CHOICES = choices.currency_choices

    name = models.CharField(max_length=128)
    media = models.FileField(upload_to='ability_media/', blank=True, null=True, validators=[validate_media])
    price = models.PositiveIntegerField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    additional_description = models.TextField(blank=True, null=True)
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES, default='everyone')
    author = models.ForeignKey(BazhayUser, related_name='abilities', on_delete=models.CASCADE)
    currency = models.CharField(max_length=50, null=True, blank=True, choices=CURRENCY_CHOICES)
    is_fully_created = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Reservation(models.Model):
    bazhay_user = models.ForeignKey(BazhayUser, related_name='reservation', on_delete=models.CASCADE)
    wish = models.ForeignKey(Wish, related_name='reservation', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.bazhay_user} reservation {self.wish.name}"
