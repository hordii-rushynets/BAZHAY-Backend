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

    class Meta:
        model = Wish

        fields = ['id', 'name', 'photo', 'video', 'price', 'link', 'description',
                  'additional_description', 'access_type', 'currency', 'created_at', 'is_fully_created', 'is_reservation', 'image_size',
                  'author', 'brand_author', 'news_author']
        read_only_fields = ['id', 'author', 'created_at', 'brand_author', 'news_author']

    def validate(self, data):
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
        return Reservation.objects.filter(wish=obj).exists()


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
    wish_id = serializers.PrimaryKeyRelatedField(queryset=Wish.objects.all(), write_only=True)

    class Meta:
        model = Wish
        fields = ['wish_id', "video", "start", "end"]

    def validate(self, attrs):
        if attrs['end'] <= attrs['start']:
            raise serializers.ValidationError("The time frame is not correct")

        wish = attrs['wish_id']
        if wish.author != self.context['request'].user:
            raise serializers.ValidationError("You are not the author of this wish.")

        attrs['wish'] = wish
        del attrs['wish_id']

        return attrs

    def create(self, validated_data):
        video = validated_data.get('video')
        start = validated_data.get('start')
        end = validated_data.get('end')
        wish = validated_data.get('wish')

        original_filename = video.name

        with VideoFileClip(video.temporary_file_path()) as clip:
            trimmed_clip = clip.subclip(start, end)
            trimmed_path = "/tmp/" + original_filename
            trimmed_clip.write_videofile(trimmed_path, codec="libx264", audio_codec="aac")

            with open(trimmed_path, "rb") as f:
                trimmed_video_content = f.read()

        wish.video.save(original_filename, ContentFile(trimmed_video_content))
        wish.save()

        return wish

