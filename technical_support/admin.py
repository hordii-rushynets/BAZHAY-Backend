from django.contrib import admin
from .models import TechnicalSupport


@admin.register(TechnicalSupport)
class TechnicalSupportAdmin(admin.ModelAdmin):
    list_display = ('question', 'user', 'get_user_info')
    search_fields = ('user__username', 'question')

    def get_user_info(self, obj):
        return f'nickname: {obj.user.username}, email: {obj.user.email}, fullname: {obj.user.get_fullname}'
    get_user_info.short_description = 'User Info'
