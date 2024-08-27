from rest_framework import serializers

from .models import Ability

from user.serializers import UpdateUserSerializers


class AbilitySerializer(serializers.ModelSerializer):
    author = UpdateUserSerializers(read_only=True)

    class Meta:
        model = Ability
        fields = ['id', 'name', 'media', 'price', 'link', 'description',
                  'additional_description', 'access_type', 'author']
        read_only_fields = ['id', 'author']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
