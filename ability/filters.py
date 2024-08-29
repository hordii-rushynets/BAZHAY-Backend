import django_filters
from .models import Wish


class WishFilter(django_filters.FilterSet):
    is_fully_created = django_filters.BooleanFilter(field_name='is_fully_created')

    class Meta:
        model = Wish
        fields = ['is_fully_created']
