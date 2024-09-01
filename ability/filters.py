import django_filters
from .models import Wish


class WishFilter(django_filters.FilterSet):
    is_fully_created = django_filters.BooleanFilter(field_name='is_fully_created')
    price = django_filters.OrderingFilter(fields=[('price', 'min'), ('-price', 'max'),])
    created = django_filters.OrderingFilter(fields=[('created_at', 'faster'), ('-created_at', 'later'),])
    access = django_filters.CharFilter(field_name='access_type')

    class Meta:
        model = Wish
        fields = ['is_fully_created', 'price', 'created', 'access']
