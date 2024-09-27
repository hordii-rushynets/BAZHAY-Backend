from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
import json


@shared_task
def send_notification_task(notification_id):
    try:
        from .models import Notification
        notification = Notification.objects.get(id=notification_id)
        if notification.send_at <= timezone.now():
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'notifications_group',
                {
                    'type': 'send_notification',
                    'message': notification.message
                }
            )
            notification.delete()
    except Notification.DoesNotExist:
        pass
