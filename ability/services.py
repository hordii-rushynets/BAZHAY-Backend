import requests
from rest_framework.exceptions import ValidationError


class CurrencyService:
    url: str = "https://open.er-api.com/v6/latest/{currency}"

    def get_exchange_rates(self, base_currency='USD') -> dict:
        """
        Get exchange rates from open.er-api.
        
        :param base_currency: currency.

        :return: dict of objects with exchange rates.
        """
        response: requests.Response = requests.get(self.url.format(currency=base_currency))
        
        if response.status_code == 200:
            data = response.json()
            return data.get('rates', {})
        else:
            raise ValidationError('Failed to fetch exchange rates')
