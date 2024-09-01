import base64
import uuid
from typing import Any, Union

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class Base64VideoField(serializers.FileField):
    """Gets data in base64 and converts it to a photo"""
    def to_internal_value(self, data: Any) -> ContentFile:
        if isinstance(data, str) and data.startswith('data:video'):
            format, videostr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(videostr), name=f'{uuid.uuid4()}.{ext}')

        return super().to_internal_value(data)


class Base64ImageField(serializers.ImageField):
    """Gets data in base64 and converts it to a photo """
    def to_internal_value(self, data: Any) -> ContentFile:
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')

        return super().to_internal_value(data)


class Base64MediaField(serializers.FileField):
    """Verifies the media type and transforms it """

    def to_internal_value(self, data: Any) -> Union[ContentFile, ValidationError]:
        if isinstance(data, str):
            if data.startswith('data:image'):
                image_field = Base64ImageField()
                return image_field.to_internal_value(data)
            elif data.startswith('data:video'):
                video_field = Base64VideoField()
                return video_field.to_internal_value(data)
            else:
                raise ValidationError('Unsupported media type. Only images and videos are allowed.')
        return super().to_internal_value(data)