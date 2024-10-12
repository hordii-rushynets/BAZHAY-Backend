from typing import Optional

from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

import ability.choices as choices

from user.models import BazhayUser
from brand.models import Brand
from news.models import News
from notifications.models import Notification

from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


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
    is_fulfilled = models.BooleanField(default=False)

    def __str__(self) -> str:
        """Return the name of the wish."""
        return self.name

    def display_author(self) -> str:
        """
        Returns a string representation of the author of the wish.

        If the wish has an author, the author's email is returned. If a brand author is present,
        the brand's name is returned. If neither is available, a dash ('-') is returned.

        :returns (str): The email of the author, the brand name, or a dash ('-').
        """
        if self.author:
            return self.author.email
        elif self.brand_author:
            return self.brand_author.name
        return '-'

    display_author.short_description = 'Author'
      

class Reservation(models.Model):
    """
    Reservation of a wish for a users.
    """
    wish = models.ForeignKey(Wish, on_delete=models.CASCADE, related_name='reservation')
    selected_user = models.ForeignKey(BazhayUser, on_delete=models.CASCADE, related_name='reservation', null=True, blank=True)

    def is_active(self):
        return False if self.selected_user else True

    def __str__(self):
        return f"wish {self.wish.name} reservation to {self.selected_user}"


class CandidatesForReservation(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='candidates')
    bazhay_user = models.ForeignKey(BazhayUser, on_delete=models.CASCADE, related_name='candidates')

    def __str__(self):
        return f"reservation {self.reservation.wish.name} candidates {self.bazhay_user}"


@receiver(post_save, sender=Reservation)
def send_notification_on_user_select(sender, instance, **kwargs):
    if instance.selected_user:
        if not instance.wish.author.is_premium():
            channel_layer = get_channel_layer()

            # For the author of the wish
            message_uk = f"Твоє бажання {instance.wish.name} зарезервували і незабаром воно виповниться!"
            message_en = f"Your wish {instance.wish.name} has been reserved and will be fulfilled soon!"
            button = [create_button('See who wants to grant my wish',
                                    'Подивитись, хто хоче виповнити моє бажання',
                                    f'/api/wish/reservation/wish={instance.wish.id}')]

            notification_data_to_autor = create_message(button, message_uk, message_en)

            async_to_sync(channel_layer.group_send)(
                f"user_{instance.wish.author.id}",
                {
                    'type': 'send_notification',
                    'message': notification_data_to_autor
                }
            )
            notification = Notification.objects.create(
                message_uk=message_uk,
                message_en=message_en,
                button=button
            )
            notification.save()
            notification.users.set([instance.wish.author])

            # For the one who reserved
            message_uk = f"Ти зарезервував бажання {instance.wish.author.username} @{instance.wish.name} і зовсім скоро ощасливиш його подарунком!"
            message_en = f"You have reserved the wish of {instance.wish.author.username} @{instance.wish.name} and will soon make him happy with a gift!"
            button = []

            notification_data_to_reserved = create_message(button, message_uk, message_en)

            async_to_sync(channel_layer.group_send)(
                f"user_{instance.selected_user.id}",
                {
                    'type': 'send_notification',
                    'message': notification_data_to_reserved
                }
            )

            notification = Notification.objects.create(
                message_uk=message_uk,
                message_en=message_en,
                button=button
            )
            notification.save()
            notification.users.set([instance.selected_user])


@receiver(post_save, sender=CandidatesForReservation)
def send_notification_on_if_new_candidate(sender, instance, created, **kwargs):
    if created:
        if instance.reservation.wish.author.is_premium():
            channel_layer = get_channel_layer()

            message_uk = f"Твоє бажання {instance.reservation.wish.name} хоче зарезервувати @{instance.bazhay_user.username}. Ти хочеш, щоб цей користувач виконав його?"
            message_en = f"Your wish {instance.reservation.wish.name} wants to reserve @{instance.bazhay_user.username}. Do you want this user to fulfill it?"
            button = [create_button('Yes',
                                    'Так',
                                    f'/api/wish/reservation/{instance.id}/select_user/',
                                    'candidate_id',
                                    f'{instance.bazhay_user.id}',
                                    'Great! Very soon you will be happier with the wish you received.',
                                    'Чудово! Зовсім скоро ти станеш щасливіше від отриманого бажання.',
                                    'It\'s a pity.But you can change your mind in the settings of this wish.',
                                    'Шкода. Проте змінити свою думку ти можеш у налаштуваннях цього бажання.'),
                      create_button('No', 'Ні'),]

            notification_data_to_author = create_message(button, message_uk, message_en)

            async_to_sync(channel_layer.group_send)(
                f"user_{instance.reservation.wish.author.id}",
                {
                    'type': 'send_notification',
                    'message': notification_data_to_author
                }
            )

            notification = Notification.objects.create(
                message_uk=message_uk,
                message_en=message_en,
                button=button
            )
            notification.save()
            notification.users.set([instance.reservation.wish.author])


def create_button(text_en: str = '', text_uk: str = '', url: str = '', name_param: str = '', value_param: str = '', ok_text_en: str = '',
                  ok_text_uk: str = '', not_ok_text_en: str = '', not_ok_text_uk: str = ''):
    return {'text_en': text_en,
            'text_uk': text_uk,
            'request': {'url': url,
                        'body': {name_param: value_param,}},
            'response_ok_text': {'ok_text_en': ok_text_en,
                                 'ok_text_uk': ok_text_uk},
            'response_not_ok_text': {'not_ok_text_en': not_ok_text_en,
                                     'not_ok_text_uk': not_ok_text_uk}
            }


def create_message(button: list, text_en: str = "", text_uk: str = "",):
    return {'message_en': text_en,
            'message_uk': text_uk,
            'button': button}
