from django.contrib import admin
from .models import Brand


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Registration in admin fot Brand"""
    exclude = ('name', 'description')
