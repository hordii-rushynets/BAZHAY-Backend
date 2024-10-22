from django.core.cache import cache
from .tasks import send_email
from django.conf import settings

import random
import string


def generate_confirmation_code(length: int = 6) -> str:
    """Generates a confirmation code, standard length 6"""
    return ''.join(random.choices(string.digits, k=length))


def save_and_send_confirmation_code(email: str) -> None:
    """Save in storage and send confirmation code"""
    confirmation_code = generate_confirmation_code()
    cache_key = f"code_{email}"
    cache.set(cache_key, confirmation_code, timeout=settings.TIME_LIFE_OTP_CODE)

    send_email.delay(email, confirmation_code)
