from rest_framework import serializers

from .models import Brand


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['slug', 'nickname', 'photo', 'name_uk', 'name_en', 'description_uk', 'description_en']
