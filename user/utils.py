from django.core.cache import cache
from .tasks import send_email

import random
import string


def generate_confirmation_code(length=6):
    return ''.join(random.choices(string.digits, k=length))


def save_and_send_confirmation_code(email):
    confirmation_code = generate_confirmation_code()
    cache_key = f"code_{email}"
    cache.set(cache_key, confirmation_code, timeout=3600)

    send_email.delay(email, confirmation_code)
