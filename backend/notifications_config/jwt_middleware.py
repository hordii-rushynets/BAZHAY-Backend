from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async
from user.models import BazhayUser


class JWTAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):
        token = self.get_token_from_scope(scope)

        if token is not None:
            user = await self.get_user_from_token(token)
            if user:
                scope['user'] = user
            else:
                scope['error'] = 'Invalid token'
        else:
            scope['error'] = 'Provide an auth token'

        return await super().__call__(scope, receive, send)

    def get_token_from_scope(self, scope):
        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b'authorization', b'').decode('utf-8')

        if auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return BazhayUser.objects.get(id=user_id)
        except BazhayUser.DoesNotExist:
            return None
