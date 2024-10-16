from rest_framework import serializers
from .models import TechnicalSupport
from user.serializers import ReturnBazhayUserSerializer


class TechnicalSupportSerializer(serializers.ModelSerializer):
    user = ReturnBazhayUserSerializer(read_only=True)

    class Meta:
        model = TechnicalSupport
        fields = ['id', 'question', 'file', 'user']
