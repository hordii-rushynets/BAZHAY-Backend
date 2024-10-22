import requests
from rest_framework.exceptions import ValidationError
from backend import settings
import redis
import Levenshtein
from datetime import timedelta


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


class PopularRequestService:
    """
    A service to manage popular request queries using Redis for storage.

    This service allows storing, retrieving, and processing popular query requests.
    It utilizes a Redis backend to track the frequency of each query and to manage
    the expiration of query records.
    """

    def __init__(self):
        self.__redis_client = redis.StrictRedis.from_url(settings.REDIS_CONNECTION_STRING % settings.RedisDatabases.DEFAULT)

    def set(self, query):
        """
        Increments the count of a given query in Redis.

        If the query does not exist, it initializes it with a count of zero and
        sets an expiration time of 7 days.

        :param query (str): The query string to be saved.
        :raises ValueError: If the query is an empty string.
        """
        redis_key = f"query:{query}"

        if not self.__redis_client.exists(redis_key):
            self.__redis_client.set(redis_key, 0)

        self.__redis_client.incr(redis_key)
        self.__redis_client.expire(redis_key, int(timedelta(days=7).total_seconds()))

    def get(self, query=None):
        """
        Retrieves popular queries or queries similar to the given query.

        If no query is provided, returns the top 5 most popular queries.
        If a query is provided, returns up to 5 similar queries based on
        Levenshtein distance.

        :param query (str, optional): The query string to find similar queries.
        :return: A list of dictionaries containing 'query' and 'count' keys.
        """
        keys = self.__redis_client.keys("query:*")

        queries_data = [{'query': key.decode().split(':')[1], 'count': int(self.__redis_client.get(key))} for key in keys]

        if not query:
            popular_queries = sorted(queries_data, key=lambda x: x['count'], reverse=True)
            return popular_queries[:5]
        else:
            similar_queries = self.__matching_check(queries_data, query)
            similar_queries = sorted(similar_queries, key=lambda x: Levenshtein.distance(query, x['query']))

            return similar_queries[:5]

    def __matching_check(self, query_list: list, query: str) -> list:
        """
        Checks for queries in the provided list that are similar to the given query.

        This method calculates the similarity ratio based on the Levenshtein distance
        and filters out queries below a threshold of 0.6. Returns a list of similar
        queries sorted by their Levenshtein distance.

        :param query_list: The list of query data to search for similar queries.
        :param query (str): The query string to compare against.
        :return: A list of similar queries sorted by Levenshtein distance.
        """

        threshold = 0.6
        similar_queries = []

        for item in query_list:
            distance = Levenshtein.distance(query, item['query'])
            max_length = max(len(query), len(item['query']))

            similarity_ratio = (max_length - distance) / max_length

            if similarity_ratio >= threshold:
                similar_queries.append(item)

        return sorted(similar_queries, key=lambda x: Levenshtein.distance(query, x['query']))


class ValidateServices:
    def __init__(self):
        self.api_secret = settings.VALIDATE_API_SECRET
        self.api_user = settings.VALIDATE_API_USER

    def photo(self):
        pass

    def text(self):
        pass

    def video(self):
        pass

