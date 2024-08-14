from rest_framework import serializers
from .models import BazhayUser


class UpdateUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = BazhayUser
        fields = ['username', 'birthday', 'sex', 'photo']

