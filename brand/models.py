from django.db import models

from ability.models import Ability
from common.models import Slug


class Brand(Slug):
    name = models.CharField(max_length=128)
    nickname = models.CharField(max_length=128, unique=True, null=True, blank=True)
    description = models.TextField()
    photo = models.ImageField()
    abilities = models.ManyToManyField(Ability)

    def __str__(self) -> str:
        return str(self.nickname)

