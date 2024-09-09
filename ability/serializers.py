from rest_framework import serializers
from django.core.exceptions import ValidationError

from .models import Wish

from user.serializers import UpdateUserSerializers
from brand.serializers import BrandSerializer
from base64_conversion import conversion


class WishSerializer(serializers.ModelSerializer):
    """Wish Serializer"""
    photo = conversion.Base64ImageField(required=False)
    video = conversion.Base64VideoField(required=False)
    author = UpdateUserSerializers(read_only=True)
    brand_author = BrandSerializer(read_only=True)

    class Meta:
        model = Wish
        fields = ['id', 'name', 'photo', 'video', 'price', 'link', 'description',
                  'additional_description', 'access_type', 'currency', 'created_at', 'is_fully_created', 'image_size',
                  'author', 'brand_author']
        read_only_fields = ['id', 'author', 'created_at', 'brand_author']

    def validate(self, data):
        user = self.context['request'].user
        is_premium = hasattr(user, 'premium') and user.premium.is_active

        # Validation of the number of wishes
        if not is_premium:
            if Wish.objects.filter(author=user).count() >= 10:
                raise ValidationError("You cannot create more than 10 wishes without a premium subscription.")

        # Validation of the view
        if not is_premium and 'access_type' in data and data['access_type'] != 'everyone':
            raise ValidationError(
                "You cannot change the access type to a non-default value without a premium subscription.")

        return data
