from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.conf import settings

from .models import Wish

from user.serializers import UpdateUserSerializers
from brand.serializers import BrandSerializer
from base64_conversion import conversion

import boto3


class WishSerializer(serializers.ModelSerializer):
    """Wish Serializer"""
    photo = conversion.Base64ImageField(required=False)
    video = conversion.Base64VideoField(required=False)
    author = UpdateUserSerializers(read_only=True)
    brand_author = BrandSerializer(read_only=True)

    class Meta:
        model = Wish
        fields = ['id', 'name', 'photo', 'video', 'price', 'link', 'description',
                  'additional_description', 'access_type', 'currency', 'created_at', 'is_fully_created', 'image_size',
                  'author', 'brand_author']
        read_only_fields = ['id', 'author', 'created_at', 'brand_author']

    def validate_photo(self, photo):
        if photo is None:
            raise ValidationError("Photo cannot be None.")

        photo_data = photo.read()
        if not photo_data:
            raise ValidationError("The uploaded photo is empty or invalid.")

        rekognition_client = boto3.client('rekognition', region_name=settings.AWS_S3_REGION_NAME)
        response = rekognition_client.detect_labels(
            Image={
                'Bytes': photo_data
            },
            MaxLabels=10
        )

        if not self.is_valid_image(response):
            raise ValidationError("The uploaded image contains inappropriate content.")
        return photo

    def validate_video(self, video):
        if video is None:
            raise ValidationError("Video cannot be None.")

        video_data = video.read()
        if not video_data:
            raise ValidationError("The uploaded photo is empty or invalid.")

        rekognition_client = boto3.client('rekognition', region_name=settings.AWS_S3_REGION_NAME)
        response = rekognition_client.start_label_detection(
            Video={
                'Bytes': video_data
            }
        )
        job_id = response['JobId']

        result = rekognition_client.get_label_detection(JobId=job_id)

        if not self.is_valid_video(result):
            raise ValidationError("The uploaded video contains inappropriate content.")
        return video

    def is_valid_image(self, rekognition_response):
        # Logic to check the image for unwanted content
        for label in rekognition_response.get('Labels', []):
            print(label)
            if label['Name'] in ['Explicit Nudity', 'Violence', 'Hate Symbols', 'Childbirth', 'Injury']:
                return False
        return True

    def is_valid_video(self, rekognition_response):
        # Logic to check the video for unwanted content
        for label_detection in rekognition_response.get('Labels', []):
            label = label_detection['Label']
            print(label)
            if label['Name'] in ['Explicit Nudity', 'Violence', 'Hate Symbols', 'Childbirth', 'Injury']:
                return False
        return True
