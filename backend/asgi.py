import os
import django

from django.core.asgi import get_asgi_application
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter

# Переміщення ініціалізації Django перед імпортом будь-яких моделей або middleware
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from .notifications_config.jwt_middleware import JWTAuthMiddleware
from notifications.consumers import NotificationConsumer

# Визначаємо застосунок ASGI
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter([
            path("ws/notifications/", NotificationConsumer.as_asgi()),
        ])
    ),
})
