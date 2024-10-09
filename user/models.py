from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


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

    Attributes:
        email (EmailField): User's email address, unique and required for authentication.
        username (CharField): User's username, unique and optional.
        birthday (DateField): User's date of birth, optional.
        view_birthday (BooleanField): Flag indicating if the user's birthday is visible.
        sex (CharField): User's gender, choices are defined in SEX_CHOICES.
        photo (ImageField): Profile photo of the user, optional.
        about_user (TextField): A text field for user description or bio, optional.
        is_already_registered (BooleanField): Flag indicating if the user is already registered.
        first_name (CharField): User's first name, optional.
        last_name (CharField): User's last name, optional.
        is_guest (BooleanField): Flag indicating if the user is a guest.
        imei (CharField): IMEI number for guest users, unique and optional.
        is_active (BooleanField): Flag indicating if the user account is active.
        is_staff (BooleanField): Flag indicating if the user has staff privileges.
        date_joined (DateTimeField): Timestamp of when the user account was created.

    Methods:
        __str__(): Returns the string representation of the user, which is the email address.
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

