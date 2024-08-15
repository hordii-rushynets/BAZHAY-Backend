from rest_framework import serializers
from .models import BazhayUser


class UpdateUserSerializers(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = BazhayUser
        fields = ['photo', 'email', 'first_name', 'last_name', 'username',
                  'birthday', 'about_user', 'sex']

