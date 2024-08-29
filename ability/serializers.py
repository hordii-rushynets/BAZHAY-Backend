from rest_framework import serializers

from .models import Wish

from user.serializers import UpdateUserSerializers
from base64_conversion import conversion


class WishSerializer(serializers.ModelSerializer):
    """Wish Serializer"""
    media = conversion.Base64MediaField(required=False)
    author = UpdateUserSerializers(read_only=True)

    class Meta:
        model = Wish
        fields = ['id', 'name', 'media', 'price', 'link', 'description',
                  'additional_description', 'access_type', 'currency', 'is_fully_created', 'author']
        read_only_fields = ['id', 'author']

