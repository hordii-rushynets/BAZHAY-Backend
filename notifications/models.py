from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

from .tasks import send_notification_task

User = get_user_model()


class Notification(models.Model):
    """
    Model representing a notification.
    """
    message = models.TextField()
    send_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(User, related_name='notifications', blank=True)
    button = models.JSONField(default=list, blank=True, null=True)
    is_button = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification: {self.message[:20]} at {self.send_at}'


@receiver(post_save, sender=Notification)
def schedule_notification(sender, instance, created, **kwargs):
    """
    Schedule a notification to be sent at the specified time.

    When a new notification is created, it calculates the delay until
    it should be sent and schedules a task to send it.

    :param sender: The model class (Notification).
    :param instance: The actual Notification instance.
    :param created: Boolean indicating if the Notification was created.
    """
    if created:
        delay = (instance.send_at - timezone.now()).total_seconds()
        send_notification_task.apply_async((instance.id,), countdown=delay)
