import requests


class CurrencyRatesService:
    """Service for currency rates"""

    def __init__(self):
        self.url = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchangenew?json'

    def get_currency_to_uah(self, currency: str) -> float | int:
        if currency == 'UAH':
            return 1.0
        response = requests.get(f'{self.url}&valcode={currency}').json()
        if response:
            return response[0].get('rate', 1.0)
        return 1.0

