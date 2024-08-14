import random
import string
from django.core.cache import cache


def generate_confirmation_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=length))


def save_confirmation_code(email):
    confirmation_code = generate_confirmation_code()
    cache_key = f"registration_code_{email}"
    cache.set(cache_key, confirmation_code, timeout=3600)

    print(f'\n\n{confirmation_code}\n\n')
