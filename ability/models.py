import mimetypes

from django.db import models
from django.core.exceptions import ValidationError

import ability.choices as choices

from user.models import BazhayUser
from brand.models import Brand
from news.models import News


def validate_video_file(file):
    if not file:
        return

    mime_type, encoding = mimetypes.guess_type(file.name)
    valid_mime_types = choices.valid_mime_types

    if mime_type not in valid_mime_types:
        raise ValidationError('Only video files are allowed.')


class Wish(models.Model):
    ACCESS_TYPE_CHOICES = choices.access_type_choices
    CURRENCY_CHOICES = choices.currency_choices

    name = models.CharField(max_length=128)
    photo = models.ImageField(upload_to='ability_media/',  blank=True, null=True,)
    video = models.FileField(upload_to='ability_media/', blank=True, null=True, validators=[validate_video_file])
    image_size = models.FloatField(blank=True, null=True)
    price = models.PositiveIntegerField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    additional_description = models.TextField(blank=True, null=True)
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES, default='everyone')
    author = models.ForeignKey(BazhayUser, related_name='abilities', on_delete=models.CASCADE, blank=True, null=True)
    brand_author = models.ForeignKey(Brand, related_name='wishes', on_delete=models.CASCADE, blank=True, null=True)
    news_author = models.ForeignKey(News, related_name='wishes', on_delete=models.CASCADE, blank=True, null=True)
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
