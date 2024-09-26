from django.db import models
from django.utils import timezone
from .tasks import send_notification


class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    send_time = models.DateTimeField()
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)  # Збереження об'єкта в базі даних

        if is_new:
            send_time_difference = (self.send_time - timezone.now()).total_seconds()
            send_notification.apply_async((self.id,), countdown=max(send_time_difference, 0))
