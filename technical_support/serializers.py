from rest_framework import serializers
from .models import TechnicalSupport


class TechnicalSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicalSupport
        fields = ['id', 'question', 'file']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data['user_nickname'] = user.username
        validated_data['user_email'] = user.email
        validated_data['user_fullname'] = user.get_fullname()

        return super().create(validated_data)
