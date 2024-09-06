import django_filters

from .models import Wish, get_currency

from django.db.models import (F, ExpressionWrapper, FloatField)


class WishFilter(django_filters.FilterSet):
    is_fully_created = django_filters.BooleanFilter(field_name='is_fully_created')
    price = django_filters.OrderingFilter(fields=[('annotated_price', 'min'), ('-annotated_price', 'max'),])
    created = django_filters.OrderingFilter(fields=[('created_at', 'faster'), ('-created_at', 'later'),])
    access = django_filters.CharFilter(field_name='access_type')
    brand = django_filters.CharFilter(field_name='brand_author__slug')
    user = django_filters.NumberFilter(field_name='author__id')

    @property
    def qs(self):
        queryset = super().qs
        cost_expression = F('price') * ExpressionWrapper(get_currency(str(F('currency'))), output_field=FloatField())
        queryset = queryset.annotate(annotated_price=cost_expression)

        return queryset

    class Meta:
        model = Wish
        fields = ['is_fully_created', 'price', 'created', 'access', 'brand', 'user']
