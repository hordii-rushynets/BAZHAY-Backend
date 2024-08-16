from django.core.cache import cache
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import BazhayUser
from .serializers import (CreateUserSerializer,
                          ConfirmCodeSerializer,
                          UpdateUserSerializers,
                          EmailUpdateSerializer,
                          EmailConfirmSerializer,
                          GuestUserSerializer,
                          ConvertGuestUserSerializer,)

from .utils import save_and_send_confirmation_code
from permission.permissions import (IsRegisteredUser,
                                    IsRegisteredUserOrReadOnly)


def is_valid(serializer):
    if serializer.is_valid():
        user = serializer.save()
        save_and_send_confirmation_code(user.email)
        return Response(status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        if request.user.is_authenticated and request.user.is_guest:
            serializer = ConvertGuestUserSerializer(data=request.data, instance=request.user)
            return is_valid(serializer)
        else:
            serializer = CreateUserSerializer(data=request.data)
            return is_valid(serializer)

    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm_code(self, request):
        serializer = ConfirmCodeSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            if user.is_guest:
                serializer = ConvertGuestUserSerializer(instance=user, data={'email': user.email})
                if serializer.is_valid():
                    serializer.save()

            cache.delete(f"code_{user.email}")

            refresh = RefreshToken.for_user(user)
            data = {
                'is_already_registered': user.is_already_registered,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            status_code = status.HTTP_200_OK if user.is_already_registered else status.HTTP_201_CREATED
            return Response(data, status=status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserViewSet(viewsets.GenericViewSet, viewsets.mixins.UpdateModelMixin, viewsets.mixins.RetrieveModelMixin):
    queryset = BazhayUser.objects.all()
    serializer_class = UpdateUserSerializers
    permission_classes = [IsRegisteredUserOrReadOnly]

    def get_object(self):
        return self.queryset.filter(id=self.request.user.id).first()


class UpdateUserEmailViewSet(viewsets.ViewSet):
    permission_classes = [IsRegisteredUser]

    def create(self, request):
        serializer = EmailUpdateSerializer(data=request.data)
        user = request.user

        if serializer.is_valid():
            new_email = serializer.validated_data['email']
            cache.set(f"pending_email_change_{user.id}", new_email, timeout=3600)
            save_and_send_confirmation_code(new_email)
            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm_code(self, request):
        user = request.user
        serializer = EmailConfirmSerializer(data=request.data, user=user)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GuestUserViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = GuestUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
