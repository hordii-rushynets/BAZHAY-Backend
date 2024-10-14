import django_filters
from django.db.models import F, Case, When, ExpressionWrapper, FloatField
from .models import Wish, AccessToViewWish, Reservation
from .services import CurrencyService


class PriceOrderingFilter(django_filters.OrderingFilter):
    """
    Custom filter to order Wish queryset by price converted to USD.

    This filter annotates the queryset with a price in USD based on the provided exchange rates and orders the results accordingly.
    """

    def filter(self, qs, value):
        """
        Annotates the queryset with the price in USD and orders by this annotated price.

        Args:
            qs (django.db.models.QuerySet): The queryset to filter.
            value (str): The ordering criteria.

        Returns:
            django.db.models.QuerySet: The filtered and ordered queryset.
        """
        currency_service: CurrencyService = CurrencyService()
        exchange_rates = currency_service.get_exchange_rates(base_currency='USD')

        return qs.annotate(
            price_in_usd=Case(
                # When currency is USD, leave the price as is
                When(currency='USD', then=F('price')),
                # When currency is in UAH, convert it to USD
                When(currency='UAH', then=ExpressionWrapper(F('price') / exchange_rates['UAH'], output_field=FloatField())),
                # When currency is in EUR, convert it to USD
                When(currency='EUR', then=ExpressionWrapper(F('price') / exchange_rates['EUR'], output_field=FloatField())),
                # Add more cases for other currencies
                When(currency='PLN', then=ExpressionWrapper(F('price') / exchange_rates['PLN'], output_field=FloatField())),
                When(currency='GBP', then=ExpressionWrapper(F('price') / exchange_rates['GBP'], output_field=FloatField())),
                When(currency='CAD', then=ExpressionWrapper(F('price') / exchange_rates['CAD'], output_field=FloatField())),
                When(currency='NOK', then=ExpressionWrapper(F('price') / exchange_rates['NOK'], output_field=FloatField())),
                When(currency='CHF', then=ExpressionWrapper(F('price') / exchange_rates['CHF'], output_field=FloatField())),
                When(currency='SEK', then=ExpressionWrapper(F('price') / exchange_rates['SEK'], output_field=FloatField())),
                output_field=FloatField(),
            )
        ).order_by('price_in_usd')


class WishFilter(django_filters.FilterSet):
    """
    FilterSet for the Wish model.

    Provides filters for `is_fully_created`, `price`, `created`, `access`, `brand`, and `user`.
    """

    is_fully_created = django_filters.BooleanFilter(field_name='is_fully_created')
    price = PriceOrderingFilter(fields=[('price', 'min'), ('-price', 'max')])
    created = django_filters.OrderingFilter(fields=[('created_at', 'faster'), ('-created_at', 'later')])
    access = django_filters.CharFilter(field_name='access_type')
    brand = django_filters.CharFilter(field_name='brand_author__slug')
    user = django_filters.NumberFilter(field_name='author__id')

    class Meta:
        model = Wish
        fields = ['is_fully_created', 'price', 'created', 'access', 'brand', 'user']


class AccessToWishFilter(django_filters.FilterSet):
    wish = django_filters.NumberFilter(field_name='wish__id')

    class Meta:
        model = AccessToViewWish
        fields = ['wish']

        
class ReservationFilter(django_filters.FilterSet):
    wish = django_filters.NumberFilter(field_name='wish__id')

    class Meta:
        model = Reservation
        fields = ['wish']
