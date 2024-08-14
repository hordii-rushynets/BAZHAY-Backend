from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_email(email, confirmation_code):
    send_mail(
        'Your Confirmation Code',
        f'Your confirmation code is {confirmation_code}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )