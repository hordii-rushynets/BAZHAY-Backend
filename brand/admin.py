from django.contrib import admin
from .models import Brand


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    filter_horizontal = ('abilities', )
    exclude = ('name', 'description')
