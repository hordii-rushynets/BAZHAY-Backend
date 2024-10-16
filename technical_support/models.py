from django.db import models
from rest_framework.serializers import ValidationError

from user.models import BazhayUser

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'avi']


def validate_image_or_video(value):
    extension = value.name.split('.')[-1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(detail=f'Allowed types are: {", ".join(ALLOWED_EXTENSIONS)}')


class TechnicalSupport(models.Model):
    question = models.TextField()
    file = models.FileField(upload_to='technical_support_files/', validators=[validate_image_or_video], blank=True, null=True)
    user = models.ForeignKey(BazhayUser, on_delete=models.CASCADE, related_name='technical_support')

    def __str__(self):
        return f'Question from {self.user.username}'
