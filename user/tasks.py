from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_confirmation_email(email, confirmation_code):
    send_mail(
        'Your confirmation code',
        f'Your confirmation code is: {confirmation_code}',
        'from@example.com',
        [email],
        fail_silently=False,
    )
