from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_email(email: str, confirmation_code: str) -> None:
    """
    Celery task to send a confirmation email with a provided code.

    This task sends an email containing the confirmation code to the specified email address.
    It uses Django's email backend to send the email.

    Args:
        email (str): The recipient's email address.
        confirmation_code (str): The confirmation code to include in the email.

    Raises:
        Exception: Any exception raised by Django's send_mail function will be propagated.
    """
    send_mail(
        'Your Confirmation Code',
        f'Your confirmation code is {confirmation_code}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
