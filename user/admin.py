from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import BazhayUser


class BazhayUserAdmin(UserAdmin):
    """Bazhay User Admin"""
    model = BazhayUser
    list_display = ('email', 'username', 'first_name', 'last_name')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    ordering = ('email',)


admin.site.register(BazhayUser, BazhayUserAdmin)
