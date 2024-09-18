from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import BazhayUser


class BazhayUserAdmin(UserAdmin):
    """
    Custom admin interface for the BazhayUser model.

    This class customizes the Django admin interface for the BazhayUser model by
    specifying which fields to display, search, filter, and order. It inherits
    from UserAdmin to leverage the built-in user management functionalities.

    Attributes:
        model: The model associated with this admin interface.
        list_display: Fields to be displayed in the list view of the admin interface.
        search_fields: Fields to be searchable in the admin interface.
        list_filter: Filters to be applied in the admin interface.
        ordering: Default ordering of objects in the admin interface.
    """
    model = BazhayUser
    list_display = ('email', 'username', 'first_name', 'last_name')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    ordering = ('email',)

# Register the custom admin interface with the Django admin site
admin.site.register(BazhayUser, BazhayUserAdmin)
