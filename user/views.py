from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from .models import BazhayUser
from .utils import save_confirmation_code
from .serializers import UpdateUserSerializers
from rest_framework.permissions import IsAuthenticated


class AuthViewSet(viewsets.ViewSet):
    def create(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        user, created = BazhayUser.objects.get_or_create(email=email)

        save_confirmation_code(email)

        user.is_already_registered = not created

        user.save()

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm_code(self, request):
        email = request.data.get('email')
        confirmation_code = request.data.get('code')

        if not email or not confirmation_code:
            return Response({'error': 'Email and confirmation code are required'}, status=status.HTTP_400_BAD_REQUEST)

        cached_code = cache.get(f"code_{email}")
        if cached_code != confirmation_code:
            return Response({'error': 'Invalid confirmation code'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = BazhayUser.objects.get(email=email)
        except BazhayUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        cache.delete(f"code_{email}")

        refresh = RefreshToken.for_user(user)
        data = {'is_already_registered': user.is_already_registered,
                'refresh': str(refresh),
                'access': str(refresh.access_token),}

        if user.is_already_registered:
            return Response(data, status=status.HTTP_200_OK)
        elif not user.is_already_registered:
            return Response(data, status=status.HTTP_201_CREATED)


class UpdateUserViewSet(viewsets.GenericViewSet, viewsets.mixins.UpdateModelMixin, viewsets.mixins.RetrieveModelMixin):
    queryset = BazhayUser.objects.all()
    serializer_class = UpdateUserSerializers
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.queryset.filter(id=self.request.user.id).first()