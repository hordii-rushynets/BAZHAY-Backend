from rest_framework import serializers
from .models import Ability

from user.serializers import UpdateUserSerializers


class AbilitySerializer(serializers.ModelSerializer):
    author = UpdateUserSerializers(read_only=True)

    class Meta:
        model = Ability
        fields = ['id', 'name', 'media', 'price', 'link', 'description', 'additional_description',
                  'author', 'access_type']
