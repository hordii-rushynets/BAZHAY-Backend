from rest_framework import serializers

from .models import Ability, AccessGroup

from user.serializers import UpdateUserSerializers
from user.models import BazhayUser


class AbilitySerializer(serializers.ModelSerializer):
    author = UpdateUserSerializers(read_only=True)

    class Meta:
        model = Ability
        fields = ['id', 'name', 'media', 'price', 'link', 'description',
                  'additional_description', 'access_type', 'chosen_groups', 'author']
        read_only_fields = ['id', 'author']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class AccessGroupSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        queryset=BazhayUser.objects.all(),
        many=True
    )

    class Meta:
        model = AccessGroup
        fields = ['id', 'name', 'members']
