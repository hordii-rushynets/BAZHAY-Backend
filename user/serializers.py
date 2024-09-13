from django.core.cache import cache
from rest_framework import serializers

from .models import BazhayUser


class CreateUserSerializer(serializers.Serializer):
    """Serializer for create or get user"""
    email = serializers.EmailField()

    def create(self, validated_data: dict) -> BazhayUser:
        """create or get user"""
        email = validated_data.get('email')
        user, created = BazhayUser.objects.get_or_create(email=email)
        if created:
            user.is_already_registered = False
        user.save()
        return user


class ConfirmCodeSerializer(serializers.Serializer):
    """Serializer check confirm code"""
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, data: dict) -> dict:
        """validate confirm code"""
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
    """Serializers for update or get user data"""
    email = serializers.EmailField(read_only=True)
    is_guest = serializers.BooleanField(read_only=True)
    photo = serializers.ImageField(read_only=True)
    subscription = serializers.SerializerMethodField()
    subscriber = serializers.SerializerMethodField()
    is_premium = serializers.SerializerMethodField()

    class Meta:
        model = BazhayUser
        fields = ['id', 'photo', 'email', 'first_name', 'last_name', 'username',
                  'birthday', 'view_birthday', 'about_user', 'sex', 'is_guest', 'is_premium', 'is_already_registered',
                  'subscription', 'subscriber']

    def get_subscription(self, obj):
        """Return the count of subscriptions"""
        return obj.subscriptions.count()

    def get_subscriber(self, obj):
        """Return the count of subscribers"""
        return obj.subscribers.count()

    def get_is_premium(self, obj):
        try:
            return obj.premium.is_active
        except:
            return False


class EmailUpdateSerializer(serializers.Serializer):
    """Serializers for update user email"""

    email = serializers.EmailField()

    def validate_email(self, value):
        """validate email"""
        if BazhayUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email is already in use')
        return value


class EmailConfirmSerializer(serializers.Serializer):
    """Serializer check confirm code"""
    code = serializers.CharField()

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def validate_code(self, value: dict) -> dict:
        """validate confirm code"""
        new_email = cache.get(f"pending_email_change_{self.user.id}")
        if not new_email:
            raise serializers.ValidationError('No pending email change found')

        cached_code = cache.get(f"code_{new_email}")
        if cached_code != value:
            raise serializers.ValidationError('Invalid confirmation code')

        return value

    def save(self) -> None:
        """Save new email"""
        new_email = cache.get(f"pending_email_change_{self.user.id}")
        self.user.email = new_email
        self.user.save()

        cache.delete(f"pending_email_change_{self.user.id}")
        cache.delete(f"code_{new_email}")


class GuestUserSerializer(serializers.Serializer):
    """Serializer for create or get guest user"""
    imei = serializers.CharField()

    def create(self, validated_data: dict) -> BazhayUser:
        imei = validated_data.get('imei')
        user, create = BazhayUser.objects.get_or_create(is_guest=True, imei=imei, email=None)
        if create:
            user.is_already_registered = False
            user.save()
        return user


class ConvertGuestUserSerializer(serializers.ModelSerializer):
    """Serializer for create user based on guest user"""
    class Meta:
        model = BazhayUser
        fields = ['email']

    def update(self, instance, validated_data: dict) -> dict:
        """Update guest user to standard user"""
        instance.email = validated_data.get('email', instance.email)
        instance.is_guest = False
        instance.save()
        return instance


class UpdateUserPhotoSerializer(serializers.ModelSerializer):
    """Serializer for update user photo"""

    photo = serializers.ImageField()

    class Meta:
        model = BazhayUser
        fields = ['photo']

