from django.db import models

from common.models import Slug


class Brand(Slug):
    """Model fot Brand"""
    name = models.CharField(max_length=128)
    nickname = models.CharField(max_length=128, unique=True, null=True, blank=True)
    description = models.TextField()
    photo = models.ImageField(upload_to='brand_photos/')
    views_number = models.PositiveIntegerField(blank=True, null=True, default=0)

    def __str__(self) -> str:
        return str(self.nickname)

