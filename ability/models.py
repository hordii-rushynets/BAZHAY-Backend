from django.db import models
from django.core.exceptions import ValidationError
from user.models import BazhayUser


def validate_media(value):
    if not value:
        return

    content_type = value.file.content_type

    if not content_type.startswith(('image/', 'video/')):
        raise ValidationError('Only images and videos are allowed.')


class AccessGroup(models.Model):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(BazhayUser, related_name='access_groups')

    def __str__(self):
        return self.name


class Ability(models.Model):
    ACCESS_TYPE_CHOICES = [
        ('subscribers', 'Subscribers'),
        ('everyone', 'Everyone'),
        ('only_me', 'Only_me'),
        ('chosen_ones', 'ChosenOnes')
    ]

    name = models.CharField(max_length=128)
    media = models.FileField(upload_to='ability_media/', blank=True, null=True, validators=[validate_media])
    price = models.PositiveIntegerField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    additional_description = models.TextField(blank=True, null=True)
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES)
    author = models.ForeignKey(BazhayUser, related_name='abilities', on_delete=models.CASCADE)
    chosen_groups = models.ManyToManyField(AccessGroup, related_name='abilities', blank=True, null=True)

    def __str__(self):
        return self.name

