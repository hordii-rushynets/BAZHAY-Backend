from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class IgnoreInvalidTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except AuthenticationFailed:
            return None
