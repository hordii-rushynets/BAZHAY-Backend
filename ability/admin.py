from django.contrib import admin
from .models import Wish


@admin.register(Wish)
class WithAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_author']
    search_fields = ['author__email', 'brand_author__nickname', 'name']
