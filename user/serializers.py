from django.core.cache import cache
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import BazhayUser, Address, PostAddress

from subscription.models import Subscription

from google.oauth2 import id_token
from google.auth.transport import requests


class CreateUserSerializer(serializers.Serializer):
    """
    Serializer for creating or retrieving a user based on the provided email.

    Fields:
        - email (str): The email address to create or get the user by.

    Methods:
        create(validated_data: dict) -> BazhayUser:
            Retrieves an existing user or creates a new user with the given email.
            If a new user is created, they are marked as not already registered.
    """
    email = serializers.EmailField()

    def create(self, validated_data: dict) -> BazhayUser:
        """
        Creates or retrieves a user using the provided email.

        Args:
            validated_data (dict): The validated data containing the user's email.

        Returns:
            BazhayUser: The user instance that was created or retrieved.
        """
        email = validated_data.get('email')
        user, created = BazhayUser.objects.get_or_create(email=email)

        if created:
            user.is_already_registered = False

        user.save()
        return user


class ConfirmCodeSerializer(serializers.Serializer):
    """
    Serializer for confirming a code sent to the user's email.

    This serializer checks the provided confirmation code against the one stored in the cache.

    Fields:
        - email (str): The email address of the user.
        - code (str): The confirmation code provided by the user (6 characters max).

    Methods:
        validate(data: dict) -> dict:
            Validates the email and confirmation code. Checks if the code matches the cached code
            and ensures the user exists. Adds the user to the validated data.
    """
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, data: dict) -> dict:
        """
        Validates the confirmation code and ensures the user exists.

        Args:
            data (dict): A dictionary containing 'email' and 'code'.

        Returns:
            dict: The validated data with the user object added.

        Raises:
            serializers.ValidationError: If the code is invalid or the user does not exist.
        """
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


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for the Address model."""
    class Meta:
        model = Address
        fields = ['id', 'country', 'region', 'city', 'street', 'post_index', 'full_name', 'phone_number']
        read_only_fields = ['id']


class PostAddressSerializer(serializers.ModelSerializer):
    """Serializer for the PostAddress model."""
    class Meta:
        model = PostAddress
        fields = ['id', 'country', 'post_service', 'city', 'nearest_branch', 'full_name', 'phone_number']
        read_only_fields = ['id']


class UpdateUserSerializers(serializers.ModelSerializer):
    """
    Serializer for retrieving or updating user data.

    This serializer provides a read-only view of the user's email, guest status, photo,
    subscription counts, subscriber counts, and subscription status. Additionally,
    it includes methods to determine if the user is premium or subscribed to another user.
    """
    email = serializers.EmailField(read_only=True)
    is_guest = serializers.BooleanField(read_only=True)
    photo = serializers.ImageField(read_only=True)
    subscription = serializers.SerializerMethodField()
    subscriber = serializers.SerializerMethodField()
    is_premium = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = BazhayUser
        fields = ['id', 'photo', 'email', 'first_name', 'last_name', 'username',
                  'birthday', 'view_birthday', 'about_user', 'sex', 'is_guest', 'is_premium', 'is_already_registered',
                  'is_subscribed', 'subscription', 'subscriber', ]

    def get_subscription(self, obj):
        """
        Returns the count of subscriptions (the number of users the given user is subscribed to).
        """
        return obj.subscriptions.count()

    def get_subscriber(self, obj):
        """
        Returns the count of subscribers (the number of users subscribed to the given user).
        """
        return obj.subscribers.count()

    def get_is_premium(self, obj):
        """
        Returns whether the user has an active premium subscription.

        If no premium subscription exists, returns False.
        """
        try:
            return obj.premium.is_active
        except:
            return False

    def get_is_subscribed(self, obj):
        """
        Returns whether the requesting user (from the context) is subscribed to the given user.

        Args:
            obj (BazhayUser): The user object to check the subscription status for.
        """
        request_user = self.context['request'].user
        return Subscription.is_subscribed(request_user, obj)


class EmailUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating the user's email.

    This serializer validates the new email, ensuring that it is not already in use by another user.

    Fields:
        - email (str): The new email address to be assigned to the user.

    Methods:
        validate_email(value: str) -> str:
            Validates the email by checking if it is already used by another user.
    """

    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        """
        Validates the provided email, ensuring it is not already in use by another user.

        Args:
            value (str): The email to be validated.

        Returns:
            str: The validated email.

        Raises:
            serializers.ValidationError: If the email is already associated with another user.
        """
        if BazhayUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email is already in use')
        return value


class EmailConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming the email change by validating a confirmation code.

    This serializer checks the provided confirmation code against the one stored in the cache
    and, if valid, updates the user's email to the new email stored in the cache.

    Fields:
        - code (str): The confirmation code provided by the user.

    Attributes:
        - user (BazhayUser): The user whose email is being confirmed and updated.

    Methods:
        validate_code(value: dict) -> dict:
            Validates the confirmation code against the cached value.

        save() -> None:
            Saves the new email for the user after successful confirmation and removes the cache.
    """
    code = serializers.CharField()

    def __init__(self, *args, **kwargs) -> None:
        """
        Initializes the serializer and extracts the user instance from the arguments.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments. The 'user' argument must be provided.
        """
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def validate_code(self, value: str) -> str:
        """
        Validates the provided confirmation code by checking it against the cached code.

        Args:
            value (str): The confirmation code to be validated.

        Returns:
            str: The validated confirmation code.

        Raises:
            serializers.ValidationError: If there is no pending email change or the code is invalid.
        """
        new_email = cache.get(f"pending_email_change_{self.user.id}")
        if not new_email:
            raise serializers.ValidationError('No pending email change found')

        cached_code = cache.get(f"code_{new_email}")
        if cached_code != value:
            raise serializers.ValidationError('Invalid confirmation code')

        return value

    def save(self) -> None:
        """
        Saves the new email to the user's profile after successful code validation.

        Updates the user's email and clears the cache entries related to the email change.
        """
        new_email = cache.get(f"pending_email_change_{self.user.id}")
        self.user.email = new_email
        self.user.save()

        cache.delete(f"pending_email_change_{self.user.id}")
        cache.delete(f"code_{new_email}")


class GuestUserSerializer(serializers.Serializer):
    """
    Serializer for creating or retrieving a guest user based on their IMEI.

    This serializer checks if a guest user exists with the given IMEI. If not,
    it creates a new guest user and marks them as not already registered.

    Fields:
        - imei (str): The unique identifier for the guest user (e.g., a device IMEI).
    """
    imei = serializers.CharField()

    def create(self, validated_data: dict) -> BazhayUser:
        """
        Creates or retrieves a guest user using the provided IMEI.

        Args:
            validated_data (dict): The data containing the IMEI.

        Returns:
            BazhayUser: The guest user instance.
        """
        imei = validated_data.get('imei')
        user, created = BazhayUser.objects.get_or_create(is_guest=True, imei=imei, email=None)

        if created:
            user.is_already_registered = False
            user.save()

        return user


class ConvertGuestUserSerializer(serializers.ModelSerializer):
    """
    Serializer for converting a guest user into a standard user.

    This serializer updates the guest user's email and changes their status
    from a guest to a standard user.

    Fields:
        - email (str): The email to be assigned to the guest user.
    """

    class Meta:
        model = BazhayUser
        fields = ['email']

    def update(self, instance, validated_data: dict) -> BazhayUser:
        """
        Updates the guest user's email and converts them into a standard user.

        Args:
            instance (BazhayUser): The guest user instance being updated.
            validated_data (dict): The data containing the new email.

        Returns:
            BazhayUser: The updated user instance.
        """
        instance.email = validated_data.get('email', instance.email)
        instance.is_guest = False
        instance.save()
        return instance


class UpdateUserPhotoSerializer(serializers.ModelSerializer):
    """
    Serializer for updating the user's profile photo.

    This serializer allows the user to upload a new profile photo.

    Fields:
        - photo (ImageField): The new profile photo to be uploaded.
    """
    photo = serializers.ImageField()

    class Meta:
        model = BazhayUser
        fields = ['photo']


class GoogleAuthSerializer(serializers.ModelSerializer):
    """
    Serializer for handling Google authorization via OAuth2.

    This serializer takes a Google OAuth2 token, validates it, and either retrieves
    an existing user or creates a new user based on the token's information.

    Fields:
        - id (int): Unique identifier of the user.
        - token (str): Google OAuth2 token (write-only field).

    Methods:
        validate(attrs: dict) -> dict:
            Validates the provided Google OAuth2 token by verifying it against Google's services.
            Ensures that the token issuer is correct. Returns the decoded token info.

        create(validated_data: dict) -> BazhayUser:
            Retrieves or creates a BazhayUser based on the email extracted from
            the validated token data. Returns the user object.
    """
    token = serializers.CharField(write_only=True)

    class Meta:
        model = BazhayUser
        fields = ['id', 'token']

    def validate(self, attrs: dict) -> dict:
        """
        Validates the Google OAuth2 token and checks the issuer.

        Args:
            attrs (dict): The input data containing the 'token'.

        Returns:
            dict: The decoded token information.

        Raises:
            serializers.ValidationError: If the token's issuer is invalid.
        """
        id_info = id_token.verify_oauth2_token(attrs.get('token'), requests.Request())

        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise serializers.ValidationError({'error': 'Wrong issuer.'})

        return id_info

    def create(self, validated_data: dict) -> BazhayUser:
        """
        Creates or retrieves a BazhayUser based on the validated token data.

        Args:
            validated_data (dict): The data returned by the validate method, which includes
                                   decoded information from the token.

        Returns:
            BazhayUser: The user object that was created or retrieved.

        Raises:
            serializers.ValidationError: If there is an error while creating or retrieving the user.
        """
        try:
            user, created = BazhayUser.objects.get_or_create(
                email=validated_data.get('email', ''),
                defaults={
                    'username': validated_data.get('email', ''),
                    'first_name': validated_data.get('given_name', ''),
                    'last_name': validated_data.get('family_name', ''),
                }
            )
            return user
        except Exception:
            raise serializers.ValidationError(detail='Something went wrong')


class ReturnBazhayUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the BazhayUser model to return user information including
    whether the requesting user is subscribed to the given user.

    """
    is_subscribed = serializers.SerializerMethodField()
    subscriber = serializers.SerializerMethodField()

    class Meta:
        model = BazhayUser
        fields = ['id', 'photo', 'username', 'first_name', 'last_name', 'is_subscribed', 'subscriber']
        read_only_fields = ['id', 'photo', 'username', 'first_name', 'last_name', 'is_subscribed', 'subscriber']

    def get_is_subscribed(self, obj: BazhayUser) -> bool:
        """
        Determines if the current user is subscribed to the given BazhayUser object.

        Args:
            obj (BazhayUser): The user object for which the subscription status is being checked.

        Returns:
            bool: True if the current user is subscribed to the provided user, False otherwise.
        """
        return Subscription.is_subscribed(self.context['request'].user, obj)

    def get_subscriber(self, obj: BazhayUser) -> int:
        """
        Returns the count of subscribers (the number of users subscribed to the given user).

        :param obj: BazhayUser object for which the number of subscribers is counted.

        """
        return obj.subscribers.count()


class BazhayUserDeletePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BazhayUser
        fields = ['photo']

    def update(self, instance, validated_data):
        if 'photo' in validated_data:
            old_photo = instance.photo
            if old_photo and old_photo != validated_data.get('photo'):
                old_photo.delete(save=False)
        return super().update(instance, validated_data)
