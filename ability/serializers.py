import os
import random
import string

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from rest_framework import serializers

from .models import Wish, Reservation

from user.serializers import UpdateUserSerializers
from brand.serializers import BrandSerializer
from moviepy.editor import VideoFileClip
from news.serializers import NewsSerializers


class WishSerializer(serializers.ModelSerializer):
    """Wish Serializer"""
    photo = serializers.ImageField(required=False)
    video = serializers.FileField(required=False)
    author = UpdateUserSerializers(read_only=True)
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
        """Validate data"""
        user = self.context['request'].user
        is_premium = hasattr(user, 'premium') and user.premium.is_active

        # Validation of the number of wishes
        if not is_premium:
            if Wish.objects.filter(author=user).count() >= 10:
                raise ValidationError("You cannot create more than 10 wishes without a premium subscription.")

        # Validation of the view
        if not is_premium and 'access_type' in data and data['access_type'] != 'everyone':
            raise ValidationError(
                "You cannot change the access type to a non-default value without a premium subscription.")

        return data

    def get_is_reservation(self, obj: Wish) -> bool:
        """Get the wish is received"""
        return Reservation.objects.filter(wish=obj).exists()

    def get_is_user_create(self, obj: Wish) -> bool:
        """Get the wish created by the user is received"""
        return True if obj.author else False

    def get_is_your_wish(self, obj: Wish) -> bool:
        """Get the wish is your"""
        return obj.author == self.context['request'].user


class ReservationSerializer(serializers.Serializer):
    """Reservation serializer"""
    bazhay_user = UpdateUserSerializers(read_only=True)
    wish = WishSerializer(read_only=True)
    wish_id = serializers.PrimaryKeyRelatedField(queryset=Wish.objects.all(), write_only=True, source='wish')

    class Meta:
        model = Reservation
        fields = ['id', 'bazhay_user', 'wish']
        read_only_fields = ['id']

    def validate(self, attrs: dict) -> dict:
        """Validate data"""
        user = self.context['request'].user
        wish = attrs.get('wish')

        if wish.author == user:
            raise serializers.ValidationError("You can't reserve your wishes")

        if Reservation.objects.filter(wish=wish).exists():
            raise serializers.ValidationError("This wish is already reserved")

        if not wish.author and (wish.news_author or wish.brand_author):
            raise serializers.ValidationError("You can't reserve this wishes")

        return attrs

    def create(self, validated_data: dict) -> Reservation:
        """Create new wish reservation"""
        user = self.context['request'].user
        reservation = Reservation.objects.create(bazhay_user=user, **validated_data)
        return reservation


class VideoSerializer(serializers.ModelSerializer):
    video = serializers.FileField(write_only=True)
    start = serializers.IntegerField(write_only=True)
    end = serializers.IntegerField(write_only=True)

    class Meta:
        model = Wish
        fields = ['id', "video", "start", "end"]

    def validate(self, attrs):
        if attrs['end'] <= attrs['start']:
            raise serializers.ValidationError("The time frame is not correct")

        user = self.context['request'].user

        if self.instance and self.instance.author != user:
            raise serializers.ValidationError("You do not have permission to modify this wish.")

        return attrs

    def update(self, instance, validated_data):
        video = validated_data.get('video')
        start = validated_data.get('start')
        end = validated_data.get('end')

        original_filename = video.name

        with VideoFileClip(video.temporary_file_path()) as clip:
            trimmed_clip = clip.subclip(start, end)
            trimmed_path = "/tmp/" + original_filename
            trimmed_clip.write_videofile(trimmed_path, codec="libx264", audio_codec="aac")

            with open(trimmed_path, "rb") as f:
                trimmed_video_content = f.read()

        instance.video.save(original_filename, ContentFile(trimmed_video_content))
        instance.save()

        return instance


class WishSerializerForNotUser(serializers.ModelSerializer):
    """Wish Serializer"""

    class Meta:
        model = Wish
        fields = ['id', 'name', 'photo', 'video', 'price', 'link', 'description',
                  'additional_description', 'currency', 'created_at', 'image_size']


class CopyWishSerializer(serializers.Serializer):
    """Copy wish serializer"""
    id = serializers.IntegerField(write_only=True)

    def validate(self, attrs):
        wish_id = attrs.get('id')
        if not wish_id:
            raise serializers.ValidationError({'id': 'ID is required'})

        try:
            original_wish = Wish.objects.get(id=wish_id)
        except Wish.DoesNotExist:
            raise serializers.ValidationError({'id': 'Wish not found'})

        attrs['original_wish'] = original_wish
        return attrs

    def generate_random_prefix(self, length=8):
        """Generates a random prefix from letters and numbers."""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def copy_file(self, file):
        """Copies a file with a random name prefix."""
        if file:
            prefix = self.generate_random_prefix()
            file_name = os.path.basename(file.name)
            return ContentFile(file.read(), name=f"{prefix}_{file_name}")
        return None

    def create(self, validated_data):
        original_wish = validated_data.pop('original_wish')

        new_wish_data = {
            'name': original_wish.name,
            'photo': self.copy_file(original_wish.photo),
            'video': self.copy_file(original_wish.video),
            'image_size': original_wish.image_size,
            'price': original_wish.price,
            'link': original_wish.link,
            'description': original_wish.description,
            'additional_description': original_wish.additional_description,
            'access_type': original_wish.access_type,
            'currency': original_wish.currency,
            'is_fully_created': original_wish.is_fully_created,
            'author': self.context['request'].user,
            'brand_author': None,
            'created_at': None
        }

        new_wish = Wish.objects.create(**new_wish_data)
        return new_wish
