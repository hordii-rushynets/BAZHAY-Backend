from modeltranslation.translator import translator, TranslationOptions
from .models import Notification


class NotificationTranslationOptions(TranslationOptions):
    """Notification Translation"""
    fields = ('message',)


translator.register(Notification, NotificationTranslationOptions)

