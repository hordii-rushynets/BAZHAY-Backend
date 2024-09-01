from django.db import models

from ability.models import Wish
from common.models import Slug


class Brand(Slug):
    """Model fot Brand"""
    name = models.CharField(max_length=128)
    nickname = models.CharField(max_length=128, unique=True, null=True, blank=True)
    description = models.TextField()
    photo = models.ImageField()
    wish = models.ManyToManyField(Wish, related_name='brand')

    def __str__(self) -> str:
        return str(self.nickname)

