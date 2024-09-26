from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'send_time', 'is_sent')
    list_filter = ('is_sent',)
    search_fields = ('title', 'message')

