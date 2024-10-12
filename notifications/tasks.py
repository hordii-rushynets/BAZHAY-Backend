from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone


@shared_task
def send_notification_task(notification_id):
    """
    Send a notification to users at the scheduled time or to a general group
    if no users are specified.

    :param notification_id: The ID of the notification to send.
    """
    from .models import Notification
    try:
        notification = Notification.objects.get(id=notification_id)
        if notification.send_at <= timezone.now():
            channel_layer = get_channel_layer()
            notification_data = {
                'message_uk': notification.message_uk,
                'message_en': notification.message_en,
                'is_button': notification.is_button
            }

            if notification.users.exists():
                for user in notification.users.all():
                    async_to_sync(channel_layer.group_send)(
                        f"user_{user.id}",
                        {
                            'type': 'send_notification',
                            'message': notification_data
                        }
                    )
            else:
                async_to_sync(channel_layer.group_send)(
                    "notifications_group",
                    {
                        'type': 'send_notification',
                        'message': notification_data
                    }
                )
    except Notification.DoesNotExist:
        pass



