from django.db import models
from ability.models import Ability


class Brand(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    photo = models.ImageField()
    abilities = models.ManyToManyField(Ability)

    def __str__(self) -> str:
        return str(self.name)

