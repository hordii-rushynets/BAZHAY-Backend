from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from rest_framework import serializers

from .models import Wish, Reservation, CandidatesForReservation

from user.serializers import ReturnBazhayUserSerializer
from brand.serializers import BrandSerializer
from moviepy.editor import VideoFileClip
from news.serializers import NewsSerializers


class WishSerializer(serializers.ModelSerializer):
    """
    Serializer for Wish model.

    Handles the serialization and validation of Wish instances, including
    fields for various attributes, user-related fields, and custom validation
    based on the user's subscription status.
    """
    photo = serializers.ImageField(required=False)
    video = serializers.FileField(required=False)
    author = ReturnBazhayUserSerializer(read_only=True)
    brand_author = BrandSerializer(read_only=True)
    news_author = NewsSerializers(read_only=True)
    is_reservation = serializers.SerializerMethodField()
    is_user_create = serializers.SerializerMethodField()
    is_your_wish = serializers.SerializerMethodField()
    is_reserved_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Wish
        fields = ['id', 'name', 'name_en', 'name_uk', 'photo', 'video', 'price', 'link', 'description',
                  'description_en', 'description_uk',
                  'additional_description', 'additional_description_en', 'additional_description_uk', 'access_type', 'currency', 'created_at', 'is_fully_created',
                  'is_reservation', 'is_user_create', 'is_your_wish', 'is_reserved_by_me', 'is_fulfilled', 'image_size', 'author', 'brand_author',
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

        if self.instance is None and not is_premium:
            if Wish.objects.filter(author=user).count() >= 10:
                raise ValidationError("You cannot create more than 10 wishes without a premium subscription.")

        if not is_premium and 'access_type' in data and data['access_type'] != 'everyone':
            raise ValidationError(
                "You cannot change the access type to a non-default value without a premium subscription.")

        return data

    def get_is_reservation(self, obj: Wish) -> bool:
        """
        Determine if the wish is reserved.

        :args obj (Wish): The wish instance.
        :returns (bool): True if the wish is reserved, otherwise False.
        """
        reservation = Reservation.objects.filter(wish=obj).first()
        if reservation and reservation.selected_user:
            return True
        return False

    def get_is_reserved_by_me(self, obj):
        """
        Check if the current user has reserved the wish.

        :args obj (Wish): The wish instance.
        :returns bool: True if the current user has reserved the wish, otherwise False.
        """
        reservation = Reservation.objects.filter(wish=obj).first()
        if reservation is None:
            return False

        return reservation.selected_user == self.context['request'].user

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
        fields = ['id', 'name', 'name_en', 'name_uk', 'photo', 'video', 'price', 'link', 'description', 'description_en', 'description_uk',
                  'additional_description', 'additional_description_en', 'additional_description_uk', 'currency',
                  'created_at', 'image_size']


class CombinedSearchSerializer(serializers.Serializer):
    """
    Serializer to combine results from Wish, BazhayUser and Brand models.
    """
    wishes = WishSerializer(many=True, read_only=True)
    users = ReturnBazhayUserSerializer(many=True, read_only=True)
    brands = BrandSerializer(many=True, read_only=True)

    class Meta:
        fields = ['wishes', 'users', 'brands']


class QuerySerializer(serializers.Serializer):
    """Serializer to query."""
    query = serializers.CharField(max_length=255, required=False)
    count = serializers.IntegerField(read_only=True)


class CandidatesForReservationSerializer(serializers.ModelSerializer):
    bazhay_user = ReturnBazhayUserSerializer(read_only=True)
    class Meta:
        model = CandidatesForReservation
        fields = ['bazhay_user']


class ReservationSerializer(serializers.ModelSerializer):
    candidates = CandidatesForReservationSerializer(many=True, read_only=True)
    selected_user = ReturnBazhayUserSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'wish', 'selected_user', 'candidates']
        read_only_fields = ['selected_user']

    def validate(self, data):
        wish = data.get('wish')
        user = self.context['request'].user

        if Reservation.objects.filter(wish=wish).exists():
            reservation = Reservation.objects.get(wish=wish)
            if not reservation.is_active:
                raise serializers.ValidationError(detail="It's already reserved for someone.")
            if CandidatesForReservation.objects.filter(reservation=reservation, bazhay_user=user).exists():
                raise serializers.ValidationError(detail="The user is already a candidate for this reservation.")

        if wish.author == user:
            raise serializers.ValidationError(detail="You cannot reserve your own wish.")

        return data

    def create(self, validated_data):
        wish = validated_data.get('wish')
        user = self.context['request'].user

        reservation, created = Reservation.objects.get_or_create(wish=wish)

        if reservation.wish.author.is_premium():
            CandidatesForReservation.objects.create(
                reservation=reservation,
                bazhay_user=user
            )
        else:
            reservation.selected_user = user
        reservation.save()

        return reservation

