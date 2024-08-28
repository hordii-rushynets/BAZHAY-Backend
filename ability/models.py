from django.db import models
from django.core.exceptions import ValidationError

import choices

from user.models import BazhayUser


def validate_media(value):
    if not value:
        return

    content_type = value.file.content_type

    if not content_type.startswith(('image/', 'video/')):
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
    currency = models.CharField(max_length=50, null=True, blank=True)
    is_fully_created = models.BooleanField(default=False)

    def __str__(self):
        return self.name

