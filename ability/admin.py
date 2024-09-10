from django.contrib import admin
from .models import Wish, Reservation


@admin.register(Wish)
class WishAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_author']
    search_fields = ['author__email', 'brand_author__nickname', 'name']


admin.site.register(Reservation)
