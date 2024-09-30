from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db.models import Q

from rest_framework import serializers

from .models import Wish, Reservation

from user.serializers import ReturnBazhayUserSerializer, BazhayUser
from brand.serializers import BrandSerializer
from moviepy.editor import VideoFileClip
from news.serializers import NewsSerializers


class WishSerializer(serializers.ModelSerializer):
    """
    Serializer for Wish model.

    Handles the serialization and validation of Wish instances, including
    fields for various attributes, user-related fields, and custom validation
    based on the user's subscription status.

    Attributes:
        photo (ImageField): Optional image field for the wish.
        video (FileField): Optional video field for the wish.
        author (ReturnBazhayUserSerializer): Serializer for the user who created the wish.
        brand_author (BrandSerializer): Serializer for the brand associated with the wish.
        news_author (NewsSerializers): Serializer for the news source associated with the wish.
        is_reservation (SerializerMethodField): Indicates if the wish is reserved.
        is_user_create (SerializerMethodField): Indicates if the wish was created by the user.
        is_your_wish (SerializerMethodField): Indicates if the wish belongs to the requesting user.

    Meta:
        model: The model associated with this serializer (Wish).
        fields: List of fields to be included in the serialized representation.
        read_only_fields: Fields that are read-only.
    """
    photo = serializers.ImageField(required=False)
    video = serializers.FileField(required=False)
    author = ReturnBazhayUserSerializer(read_only=True)
    brand_author = BrandSerializer(read_only=True)
    news_author = NewsSerializers(read_only=True)
    is_reservation = serializers.SerializerMethodField()
    is_user_create = serializers.SerializerMethodField()
    is_your_wish = serializers.SerializerMethodField()

    class Meta:
        model = Wish
        fields = ['id', 'name', 'photo', 'video', 'price', 'link', 'description',
                  'additional_description', 'access_type', 'currency', 'created_at', 'is_fully_created',
                  'is_reservation', 'is_user_create', 'is_your_wish', 'image_size', 'author', 'brand_author',
                  'news_author']
        read_only_fields = ['id', 'author', 'created_at', 'brand_author', 'news_author']

    def validate(self, data: dict) -> dict:
        """
        Validate wish data.

        Checks if the user has a premium subscription and enforces limits on the number
        of wishes or access type changes based on the subscription status.

        Args:
            data (dict): The data to be validated.

        Returns:
            dict: The validated data.

        Raises:
            ValidationError: If validation checks fail.
        """
        user = self.context['request'].user
        is_premium = hasattr(user, 'premium') and user.premium.is_active

        # Validate the number of wishes for non-premium users
        if not is_premium:
            if Wish.objects.filter(author=user).count() >= 10:
                raise ValidationError("You cannot create more than 10 wishes without a premium subscription.")

        # Validate the access type for non-premium users
        if not is_premium and 'access_type' in data and data['access_type'] != 'everyone':
            raise ValidationError(
                "You cannot change the access type to a non-default value without a premium subscription.")

        return data

    def get_is_reservation(self, obj: Wish) -> bool:
        """
        Determine if the wish is reserved.

        Args:
            obj (Wish): The wish instance.

        Returns:
            bool: True if the wish is reserved, otherwise False.
        """
        return Reservation.objects.filter(wish=obj).exists()

    def get_is_user_create(self, obj: Wish) -> bool:
        """
        Determine if the wish was created by the user.

        Args:
            obj (Wish): The wish instance.

        Returns:
            bool: True if the wish was created by the user, otherwise False.
        """
        return True if obj.author else False

    def get_is_your_wish(self, obj: Wish) -> bool:
        """
        Determine if the wish belongs to the requesting user.

        Args:
            obj (Wish): The wish instance.

        Returns:
            bool: True if the wish belongs to the requesting user, otherwise False.
        """
        return obj.author == self.context['request'].user


class ReservationSerializer(serializers.Serializer):
    """
    Serializer for creating and validating reservations for wishes.

    This serializer handles the creation of reservations, including validation
    to ensure that users cannot reserve their own wishes or reserve a wish that
    is already reserved. It also checks that certain conditions are met before
    allowing the reservation.

    Attributes:
        bazhay_user (ReturnBazhayUserSerializer): The user making the reservation.
        wish (WishSerializer): The wish being reserved.
        wish_id (PrimaryKeyRelatedField): The ID of the wish being reserved, used for creating reservations.

    Meta:
        model: The model associated with this serializer (Reservation).
        fields: List of fields to be included in the serialized representation.
        read_only_fields: Fields that are read-only.
    """
    bazhay_user = ReturnBazhayUserSerializer(read_only=True)
    wish = WishSerializer(read_only=True)
    wish_id = serializers.PrimaryKeyRelatedField(queryset=Wish.objects.all(), write_only=True, source='wish')

    class Meta:
        model = Reservation
        fields = ['id', 'bazhay_user', 'wish', 'wish_id']
        read_only_fields = ['id']

    def validate(self, attrs: dict) -> dict:
        """
        Validate reservation data.

        Ensures that the user is not reserving their own wish, that the wish is not
        already reserved, and that the wish meets certain conditions before allowing
        the reservation.

        Args:
            attrs (dict): The data to be validated.

        Returns:
            dict: The validated data.

        Raises:
            serializers.ValidationError: If any validation checks fail.
        """
        user = self.context['request'].user
        wish = attrs.get('wish')

        if wish.author == user:
            raise serializers.ValidationError("You can't reserve your own wishes.")

        if Reservation.objects.filter(wish=wish).exists():
            raise serializers.ValidationError("This wish is already reserved.")

        if not wish.author and (wish.news_author or wish.brand_author):
            raise serializers.ValidationError("You can't reserve this wish.")

        return attrs

    def create(self, validated_data: dict) -> Reservation:
        """
        Create a new reservation.

        Args:
            validated_data (dict): The validated data used to create the reservation.

        Returns:
            Reservation: The newly created reservation instance.
        """
        user = self.context['request'].user
        reservation = Reservation.objects.create(bazhay_user=user, **validated_data)
        return reservation


class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for handling video uploads and updates.

    This serializer allows users to upload a video, specify a start and end time,
    and then process the video to create a trimmed version. It performs validation
    on the provided time frame and checks user permissions.

    Attributes:
        video (FileField): The video file to be uploaded.
        start (IntegerField): Start time (in seconds) for video trimming.
        end (IntegerField): End time (in seconds) for video trimming.

    Meta:
        model: The model associated with this serializer (Wish).
        fields: List of fields to be included in the serialized representation.
    """
    video = serializers.FileField(write_only=True)
    start = serializers.IntegerField(write_only=True)
    end = serializers.IntegerField(write_only=True)

    class Meta:
        model = Wish
        fields = ['id', 'video', 'start', 'end']

    def validate(self, attrs):
        """
        Validate the provided data.

        Checks that the end time is greater than the start time and that the user
        has permission to modify the video associated with the wish.

        Args:
            attrs (dict): The data to be validated.

        Returns:
            dict: The validated data.

        Raises:
            serializers.ValidationError: If the end time is less than or equal to the start time,
                                          or if the user does not have permission to modify the wish.
        """
        if attrs['end'] <= attrs['start']:
            raise serializers.ValidationError("The time frame is not correct")

        user = self.context['request'].user

        if self.instance and self.instance.author != user:
            raise serializers.ValidationError("You do not have permission to modify this wish.")

        return attrs

    def update(self, instance, validated_data):
        """
        Update the wish with a trimmed version of the uploaded video.

        Args:
            instance (Wish): The wish instance to be updated.
            validated_data (dict): The validated data including the video and time frame.

        Returns:
            Wish: The updated wish instance.
        """
        video = validated_data.get('video')
        start = validated_data.get('start')
        end = validated_data.get('end')

        original_filename = video.name

        # Process the video
        with VideoFileClip(video.temporary_file_path()) as clip:
            trimmed_clip = clip.subclip(start, end)
            trimmed_path = "/tmp/" + original_filename
            trimmed_clip.write_videofile(trimmed_path, codec="libx264", audio_codec="aac")

            # Read and save the trimmed video
            with open(trimmed_path, "rb") as f:
                trimmed_video_content = f.read()

        instance.video.save(original_filename, ContentFile(trimmed_video_content))
        instance.save()

        return instance


class WishSerializerForNotUser(serializers.ModelSerializer):
    """
    Serializer for the Wish model to handle serialization and deserialization of wish objects.

    This serializer is used to convert Wish model instances into JSON format and vice versa.
    It includes the fields that are relevant for views where the user is not authenticated or does not
    need to see or modify all the fields.
    """
    class Meta:
        model = Wish
        fields = ['id', 'name', 'photo', 'video', 'price', 'link', 'description',
                  'additional_description', 'currency', 'created_at', 'image_size']


class CombinedSearchSerializer(serializers.Serializer):
    """Serializer to combine results from Wish and BazhayUser models."""
    wishes = WishSerializer(many=True, read_only=True)
    users = ReturnBazhayUserSerializer(many=True, read_only=True)

    class Meta:
        fields = ['wishes', 'users']

