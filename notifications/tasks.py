from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@shared_task
def send_notification(notification_id):
    from .models import Notification

    try:
        notification = Notification.objects.get(id=notification_id)

        notification_data = {
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'sent_time': notification.send_time.isoformat(),
        }

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            "notifications",
            {
                "type": "send.notification",
                "notification": notification_data
            }
        )
        notification.is_sent = True
        notification.save()

    except Notification.DoesNotExist:
        print(f"Notification with id {notification_id} does not exist.")
