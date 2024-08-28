from rest_framework import serializers

from .models import Wish

from user.serializers import UpdateUserSerializers
from base64_conversion import conversion


class WishSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField()

    class Meta:
        model = Wish
        fields = ['id', 'name', 'media', 'price', 'link', 'description',
                  'additional_description', 'access_type', 'currency', 'is_fully_created', 'author']
        read_only_fields = ['id', 'author']

    def get_media(self, obj):
        # If needed, modify this method to return the media URL or base64 data
        # depending on the requirements of your frontend
        request = self.context.get('request')
        if obj.media and request:
            return request.build_absolute_uri(obj.media.url)
        return None

    def to_internal_value(self, data):
        if 'media' in data:
            media = data.get('media')
            if isinstance(media, str):
                if media.startswith('data:image') or media.startswith('data:video'):
                    if media.startswith('data:image'):
                        media_field = conversion.Base64ImageField()
                    elif media.startswith('data:video'):
                        media_field = conversion.Base64VideoField()
                    data['media'] = media_field.to_internal_value(media)
        return super().to_internal_value(data)

