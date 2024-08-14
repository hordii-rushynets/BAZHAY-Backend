from django.db.models import Q
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import BazhayUser
from django.core.cache import cache
from .utils import save_confirmation_code


class RegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = BazhayUser
        fields = ['email', 'password', 'username']

    def validate_email(self, value):
        cache_key = f"registration_attempt_{value}"
        if cache.get(cache_key):
            raise serializers.ValidationError("Confirmation code already sent to this email.")
        return value

    def create(self, validated_data):
        user = BazhayUser.objects.create_user(
            email=validated_data.get('email'),
            password=validated_data.get('password'),
            username=validated_data.get('username')
        )
        user.is_active = False
        user.save()

        save_confirmation_code(validated_data.get('email'))
        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        if identifier and password:
            user = BazhayUser.objects.filter(Q(email=identifier) | Q(username=identifier)).first()
            if user and user.check_password(password):
                if not user.is_active:
                    raise serializers.ValidationError(_("Account is not active. Please confirm your email."))
                data['user'] = user
            else:
                raise serializers.ValidationError(_("Invalid credentials."))
        else:
            raise serializers.ValidationError(_("Must include 'identifier' and 'password'."))

        return data

