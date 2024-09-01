from django.db import models

from common.models import Slug
from ability.models import Wish


class News(Slug):
    """News model"""
    photo = models.ImageField(upload_to='news_photos/')
    title = models.CharField()
    description = models.TextField()
    wish = models.ManyToManyField(Wish, related_name='news')
    priority = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'

    def __str__(self) -> str:
        return str(self.title)
