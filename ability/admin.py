from django.contrib import admin
from .models import Wish, Reservation


@admin.register(Wish)
class WishAdmin(admin.ModelAdmin):
    """
    Admin interface for the Wish model.

    Displays a list of wishes with the following fields:
    - name
    - display_author

    Provides search functionality on:
    - author's email
    - brand author's nickname
    - wish's name
    """
    list_display = ['name', 'display_author']
    search_fields = ['author__email', 'brand_author__nickname', 'name']


admin.site.register(Reservation)
