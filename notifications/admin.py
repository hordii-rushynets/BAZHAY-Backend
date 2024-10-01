from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for managing notifications."""
    list_display = ['message', 'send_at', 'created_at']
    ordering = ['send_at']
    filter_horizontal = ('users',)




