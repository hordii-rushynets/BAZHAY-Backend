from django.core.cache import cache
from rest_framework import serializers
import uuid

from .models import BazhayUser


class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data.get('email')
        user, created = BazhayUser.objects.get_or_create(email=email)
        user.is_already_registered = not created
        user.save()
        return user


class ConfirmCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        confirmation_code = data.get('code')

        cached_code = cache.get(f"code_{email}")
        if cached_code != confirmation_code:
            raise serializers.ValidationError({'code': 'Invalid confirmation code'})

        try:
            user = BazhayUser.objects.get(email=email)
        except BazhayUser.DoesNotExist:
            raise serializers.ValidationError({'email': 'User not found'})

        data['user'] = user
        return data


class UpdateUserSerializers(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    is_guest = serializers.BooleanField(read_only=True)

    class Meta:
        model = BazhayUser
        fields = ['photo', 'email', 'first_name', 'last_name', 'username',
                  'birthday', 'about_user', 'sex', 'is_guest']


class EmailUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if BazhayUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email is already in use')
        return value


class EmailConfirmSerializer(serializers.Serializer):
    code = serializers.CharField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def validate_code(self, value):
        new_email = cache.get(f"pending_email_change_{self.user.id}")
        if not new_email:
            raise serializers.ValidationError('No pending email change found')

        cached_code = cache.get(f"code_{new_email}")
        if cached_code != value:
            raise serializers.ValidationError('Invalid confirmation code')

        return value

    def save(self):
        new_email = cache.get(f"pending_email_change_{self.user.id}")
        self.user.email = new_email
        self.user.save()

        cache.delete(f"pending_email_change_{self.user.id}")
        cache.delete(f"code_{new_email}")


class GuestUserSerializer(serializers.Serializer):
    def create(self, validated_data):
        guest_email = f"guest_{uuid.uuid4().hex}@example.com"
        user = BazhayUser.objects.create(is_guest=True, email=guest_email)
        user.is_already_registered = False
        user.save()
        return user


class ConvertGuestUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BazhayUser
        fields = ['email']

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.is_guest = False
        instance.is_already_registered = False
        instance.save()
        return instance
