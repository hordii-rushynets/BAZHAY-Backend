from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


SEX_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]


class BazhayUserManager(BaseUserManager):
    def create_user(self, email, password=None, username=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('username', email)

        return self.create_user(email, password, **extra_fields)


class BazhayUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for Bazhay application.

    This model extends Django's AbstractBaseUser and PermissionsMixin to provide
    custom fields and methods for user management. It supports user registration,
    guest user functionality, and additional user attributes.
    """
    email = models.EmailField(_('email address'), unique=True, null=True)
    username = models.CharField(_('username'), max_length=150, unique=True, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    view_birthday = models.BooleanField(default=True, blank=True, null=True)
    sex = models.CharField(max_length=50, choices=SEX_CHOICES, blank=True, null=True)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    about_user = models.TextField(default=None, blank=True, null=True)
    is_already_registered = models.BooleanField(default=False)
    first_name = models.CharField(max_length=128, default=None, blank=True, null=True)
    last_name = models.CharField(max_length=128, default=None, blank=True, null=True)

    is_guest = models.BooleanField(default=False)
    imei = models.CharField(max_length=100, unique=True, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now, blank=True, null=True)

    objects = BazhayUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self) -> str:
        """Returns the string representation of the user, which is the email address."""
        return str(self.email)

    def is_premium(self):
        try:
            return self.premium.is_active
        except:
            return False


class BaseAddress(models.Model):
    """ Abstract model representing a basic address with user, country, city, full name, and phone number fields.
    This model serves as a base for more specific address types."""
    user = models.ForeignKey(BazhayUser, on_delete=models.CASCADE)
    country = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    full_name = models.CharField(max_length=200, blank=True, default='')
    phone_number = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        abstract = True


class Address(BaseAddress):
    """Model representing a more detailed address, extending BaseAddress to include region, street, and post index."""
    region = models.CharField(max_length=100, blank=True, default='')
    street = models.CharField(max_length=100, blank=True, default='')
    post_index = models.CharField(max_length=50, blank=True, default='')

    def __str__(self):
        return f"{self.user.username}, {self.country} {self.region} {self.city}"


class PostAddress(BaseAddress):
    """Model representing a postal address, extending BaseAddress to include post service and nearest branch."""
    post_service = models.CharField(max_length=100, blank=True, default='')
    nearest_branch = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return f"{self.user.username}, {self.nearest_branch}"


class BaseAccessToAddress(models.Model):
    bazhay_user = models.ForeignKey('BazhayUser', on_delete=models.CASCADE, related_name='%(class)s_given_access_to_address')
    asked_bazhay_user = models.ForeignKey('BazhayUser', on_delete=models.CASCADE, related_name='%(class)s_requested_access_to_address')
    is_approved = models.BooleanField(default=False)
    is_not_approved = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.asked_bazhay_user} asked access to {self.bazhay_user}"


class AccessToAddress(BaseAccessToAddress):
    pass


class AccessToPostAddress(BaseAccessToAddress):
    pass


@receiver(post_save, sender=AccessToPostAddress)
def send_notification_access_to_address(sender, instance, created, **kwargs):
    from ability.models import create_message, create_button
    from notifications.models import Notification

    if created:
        message_uk = f'@{instance.bazhay_user.username} хоче тобі надіслати подарунок і запитує дозвіл подивитись адресу твого поштового відділення. Ти хочеш, щоб цей користувач побачив її?'
        message_en = f'@{instance.bazhay_user.username} wants to send you a gift and asks permission to see your post office address. Do you want this user to see it?'

        buttons = [
            create_button(
                'Yes',
                'Так',
                f'api/account/get-access-post-address/{instance.id}/approved/',
                '',
                '',
                'That\'s great! Very soon you will be happier with the wish you have received.',
                'Чудово! Зовсім скоро ти станеш щасливіше від отриманого бажання.',
                '',
                '',
            ),
            create_button(
                'No',
                'Ні'
            )
        ]

        notification_to_send = create_message(button=buttons, text_en=message_en, text_uk=message_uk)
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"user_{instance.asked_bazhay_user.id}",
            {
                'type': 'send_notification',
                'message': notification_to_send
            }
        )

        notification = Notification.objects.create(
            message_uk=message_uk,
            message_en=message_en,
            button=buttons
        )
        notification.save()
        notification.users.set([instance.reservation.wish.author])


@receiver(post_save, sender=AccessToAddress)
def send_notification_access_to_address(sender, instance, created, **kwargs):
    from ability.models import create_message, create_button
    from notifications.models import Notification

    if created:
        message_uk = f'@{instance.bazhay_user.username} хоче тобі надіслати подарунок і запитує дозвіл подивитись твою адресу. Ти хочеш, щоб цей користувач побачив її?'
        message_en = f'@{instance.bazhay_user.username} wants to send you a gift and asks permission to see your address. Do you want this user to see it?n '

        buttons = [
            create_button(
                'Yes',
                'Так',
                f'api/account/get-access-address/{instance.id}/approved/',
                '',
                '',
                'That\'s great! Very soon you will be happier with the wish you have received.',
                'Чудово! Зовсім скоро ти станеш щасливіше від отриманого бажання.',
                '',
                '',
            ),
            create_button(
                'No',
                'Ні'
            )
        ]

        notification_to_send = create_message(button=buttons, text_en=message_en, text_uk=message_uk)
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"user_{instance.asked_bazhay_user.id}",
            {
                'type': 'send_notification',
                'message': notification_to_send
            }
        )

        notification = Notification.objects.create(
            message_uk=message_uk,
            message_en=message_en,
            button=buttons
        )
        notification.save()
        notification.users.set([instance.reservation.wish.author])