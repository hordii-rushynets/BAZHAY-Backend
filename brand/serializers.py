from rest_framework import serializers

from .models import Brand

from ability.serializers import AbilitySerializer


class BrandSerializer(serializers.ModelSerializer):
    abilities = AbilitySerializer(read_only=True, many=True)

    class Meta:
        model = Brand
        fields = ['photo', 'name_uk', 'name_en', 'description_uk', 'description_en', 'abilities']
