from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .tasks import send_notification_task
from .message_text import welcome_message_uk, welcome_message_en

from user.models import BazhayUser


class Notification(models.Model):
    message = models.TextField()
    send_at = models.DateTimeField(default=timezone.now())
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification: {self.message[:20]} at {self.send_at}'


@receiver(post_save, sender=Notification)
def schedule_notification(sender, instance, created, **kwargs):
    if created:
        delay = (instance.send_at - timezone.now()).total_seconds()
        send_notification_task.apply_async((instance.id,), countdown=delay)


@receiver(post_save, sender=BazhayUser)
def send_welcome_notification(sender, instance, created, **kwargs):
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
