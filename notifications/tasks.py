from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone


@shared_task
def send_notification_task(notification_id):
    """
    Send a notification to users at the scheduled time.

    Retrieves the notification by its ID and sends it to all associated users
    via their WebSocket group if the scheduled time has been reached.

    :param notification_id: The ID of the notification to send.
    """
    from .models import Notification
    try:
        notification = Notification.objects.get(id=notification_id)
        if notification.send_at <= timezone.now():
            channel_layer = get_channel_layer()
            notification_data = {
                'id': notification.id,
                'message': notification.message,
            }
            for user in notification.users.all():
                async_to_sync(channel_layer.group_send)(
                    f"user_{user.id}",
                    {
                        'type': 'send_notification',
                        'message': notification_data
                    }
                )
    except Notification.DoesNotExist:
        pass


