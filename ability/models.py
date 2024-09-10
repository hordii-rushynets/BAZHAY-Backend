from django.db import models
from django.core.exceptions import ValidationError

import ability.choices as choices

from user.models import BazhayUser
from brand.models import Brand


def validate_media(value):
    if not value:
        return

    content_type = getattr(value, 'content_type', None)
    if content_type and not content_type.startswith(('image/', 'video/')):
        raise ValidationError('Only images and videos are allowed.')


class Wish(models.Model):
    ACCESS_TYPE_CHOICES = choices.access_type_choices
    CURRENCY_CHOICES = choices.currency_choices
    IMAGE_SIZE_CHOICES = choices.image_size_choices

    name = models.CharField(max_length=128)
    media = models.FileField(upload_to='ability_media/', blank=True, null=True, validators=[validate_media])
    image_size = models.CharField(max_length=10, choices=IMAGE_SIZE_CHOICES, blank=True, null=True)
    price = models.PositiveIntegerField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    additional_description = models.TextField(blank=True, null=True)
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES, default='everyone')
    author = models.ForeignKey(BazhayUser, related_name='abilities', on_delete=models.CASCADE, blank=True, null=True)
    brand_author = models.ForeignKey(Brand, related_name='wishes', on_delete=models.CASCADE, blank=True, null=True)
    currency = models.CharField(max_length=50, null=True, blank=True,  choices=CURRENCY_CHOICES)
    is_fully_created = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name

    def display_author(self):
        if self.author:
            return self.author.email
        elif self.brand_author:
            return self.brand_author.name
        return '-'

    display_author.short_description = 'Author'
      

class Reservation(models.Model):
    bazhay_user = models.ForeignKey(BazhayUser, related_name='reservation', on_delete=models.CASCADE)
    wish = models.ForeignKey(Wish, related_name='reservation', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.bazhay_user} reservation {self.wish.name}"
