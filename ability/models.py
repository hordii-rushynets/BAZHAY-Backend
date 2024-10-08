from typing import Optional

from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

import ability.choices as choices

from user.models import BazhayUser
from brand.models import Brand
from news.models import News


def validate_video_file(file: Optional[UploadedFile]) -> None:
    """
    Validates that the uploaded file is a video file based on its MIME type.

    Args:
        file (Optional[UploadedFile]): The uploaded file to validate.

    Raises:
        ValidationError: If the file is not a valid video MIME type.
    """
    if file is None:
        return

    valid_mime_types = choices.valid_mime_types
    file_type = file.content_type
    if file_type not in valid_mime_types:
        raise ValidationError('Only video files are allowed.')


class Wish(models.Model):
    """
    Model representing a wish or request for a specific item or experience.

    """
    ACCESS_TYPE_CHOICES = choices.access_type_choices
    CURRENCY_CHOICES = choices.currency_choices

    name = models.CharField(max_length=128)
    photo = models.ImageField(upload_to='ability_media/',  blank=True, null=True,)
    video = models.FileField(upload_to='ability_media/', blank=True, null=True, validators=[validate_video_file])
    image_size = models.FloatField(blank=True, null=True)
    price = models.PositiveIntegerField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    additional_description = models.TextField(blank=True, null=True)
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPE_CHOICES, default='everyone')
    author = models.ForeignKey(BazhayUser, related_name='abilities', on_delete=models.CASCADE, blank=True, null=True)
    brand_author = models.ForeignKey(Brand, related_name='wishes', on_delete=models.CASCADE, blank=True, null=True)
    news_author = models.ForeignKey(News, related_name='wishes', on_delete=models.CASCADE, blank=True, null=True)
    currency = models.CharField(max_length=50, null=True, blank=True,  choices=CURRENCY_CHOICES)
    is_fully_created = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    views_number = models.PositiveIntegerField(blank=True, null=True, default=0)

    def __str__(self) -> str:
        """Return the name of the wish."""
        return self.name

    def display_author(self) -> str:
        """
        Returns a string representation of the author of the wish.

        If the wish has an author, the author's email is returned. If a brand author is present,
        the brand's name is returned. If neither is available, a dash ('-') is returned.

        Returns:
            str: The email of the author, the brand name, or a dash ('-').
        """
        if self.author:
            return self.author.email
        elif self.brand_author:
            return self.brand_author.name
        return '-'

    display_author.short_description = 'Author'
      

class Reservation(models.Model):
    """
    Reservation of a wish for a user.
    """
    bazhay_user = models.ForeignKey(BazhayUser, related_name='reservations', on_delete=models.CASCADE)
    wish = models.ForeignKey(Wish, related_name='reservations', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    selected_giver = models.ForeignKey(BazhayUser, null=True, blank=True, related_name='selected_giver', on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.bazhay_user} reservation {self.wish.name}"

