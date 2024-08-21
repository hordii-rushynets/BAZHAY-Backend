from django.db import models
from django.core.exceptions import ValidationError
from user.models import BazhayUser


def validate_media(value):
    if not value:
        return
    if not value.content_type.startswith(('image/', 'video/')):
        raise ValidationError('Only images and videos are allowed.')


class Subscription(models.Model):
    user = models.ForeignKey(BazhayUser, related_name='subscriptions', on_delete=models.CASCADE)
    subscribed_to = models.ForeignKey(BazhayUser, related_name='subscribers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'subscribed_to')


class Ability(models.Model):
    ACCESS_TYPE_CHOICES = [
        ('subscribers', 'Subscribers'),
        ('everyone', 'Everyone'),
    ]

    name = models.CharField(max_length=128)
    media = models.FileField(upload_to='media/', blank=True, null=True, validators=[validate_media])
    price = models.PositiveIntegerField()
    link = models.URLField()
    description = models.TextField()
    additional_description = models.TextField()
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES, default='subscribers')
    author = models.ForeignKey(BazhayUser, related_name='abilities', on_delete=models.CASCADE)

