from django.contrib import admin
from .models import TechnicalSupport


@admin.register(TechnicalSupport)
class TechnicalSupportAdmin(admin.ModelAdmin):
    search_fields = ('user_nickname', 'question', 'user_email', 'user_fullname')
