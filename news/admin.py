from django.contrib import admin
from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """News admin"""
    list_display = ['slug', 'title', 'priority']
    filter_horizontal = ['wish']
    search_fields = ['slug', 'title', 'wish__name', 'priority']
    exclude = ('title', 'description')


