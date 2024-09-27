from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

from .tasks import send_notification_task


class Notification(models.Model):
    message = models.TextField()
    send_at = models.DateTimeField(blank=True, null=True, default=timezone.now())
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification: {self.message[:20]} at {self.send_at}'


@receiver(post_save, sender=Notification)
def schedule_notification(sender, instance, created, **kwargs):
    if created:
        delay = (instance.send_at - timezone.now()).total_seconds()
        send_notification_task.apply_async((instance.id,), countdown=delay)
