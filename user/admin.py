from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import BazhayUser, Address, PostAddress


class BazhayUserAdmin(UserAdmin):
    """
    Custom admin interface for the BazhayUser model.
    """
    model = BazhayUser
    list_display = ('email', 'username', 'first_name', 'last_name')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    ordering = ('email',)


# Register the custom admin interface with the Django admin site
admin.site.register(BazhayUser, BazhayUserAdmin)
admin.site.register(Address)
admin.site.register(PostAddress)
