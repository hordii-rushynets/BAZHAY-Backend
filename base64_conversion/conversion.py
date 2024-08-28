from django.core.files.base import ContentFile
from rest_framework import serializers
import base64
import uuid


class Base64VideoField(serializers.FileField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:video'):
            format, videostr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(videostr), name=f'{uuid.uuid4()}.{ext}')

        return super().to_internal_value(data)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')

        return super().to_internal_value(data)