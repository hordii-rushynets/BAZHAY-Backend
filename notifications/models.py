from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .tasks import send_notification_task
from .message_text import welcome_message_uk, welcome_message_en

User = get_user_model()


class Notification(models.Model):
    """
    Model representing a notification.
    """
    message = models.TextField()
    send_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(User, related_name='notifications', blank=True)  # Link to users

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


@receiver(post_save, sender=User)
def send_welcome_notification(sender, instance, created, **kwargs):
    """
    Send a welcome notification to a new user.

    When a new user is created, it sends a welcome notification to the user's
    personal WebSocket group.

    :param sender: The model class (User).
    :param instance: The actual User instance.
    :param created: Boolean indicating if the User was created.
    """

    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.id}",
            {
                'type': 'send_notification',
                'message': {
                    'welcome_message_uk': welcome_message_uk,
                    'welcome_message_en': welcome_message_en
                }
            }
        )