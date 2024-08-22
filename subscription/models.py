from django.db import models
from user.models import BazhayUser


class Subscription(models.Model):
    user = models.ForeignKey(BazhayUser, related_name='subscriptions', on_delete=models.CASCADE)
    subscribed_to = models.ForeignKey(BazhayUser, related_name='subscribers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'subscribed_to')

    def __str__(self):
        return f"{self.user.email} subscribed to {self.subscribed_to.email}"
