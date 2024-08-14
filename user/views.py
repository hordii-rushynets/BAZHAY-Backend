from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegistrationSerializer, LoginSerializer
from .models import BazhayUser
from django.core.cache import cache
from rest_framework.decorators import action


#class RegistrationViewSet(viewsets.ModelViewSet):
#    queryset = BazhayUser.objects.all()
#    serializer_class = RegistrationSerializer
#
#    def create(self, request, *args, **kwargs):
#        serializer = self.get_serializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(status=status.HTTP_200_OK)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#    @action(detail=False, methods=['post'], url_path='confirm')
#    def confirm_email(self, request):
#        email = request.data.get('email')
#        confirmation_code = request.data.get('code')
#
#        cache_key = f"registration_code_{email}"
#        cached_code = cache.get(cache_key)
#        print(cached_code)
#
#        if cached_code is None:
#            return Response({"error": "Invalid or expired confirmation code."}, status=status.HTTP_400_BAD_REQUEST)
#
#        if confirmation_code != cached_code:
#            return Response({"error": "Incorrect confirmation code."}, status=status.HTTP_400_BAD_REQUEST)
#
#        try:
#            user = BazhayUser.objects.get(email=email)
#            user.is_active = True
#            user.save()
#        except BazhayUser.DoesNotExist:
#            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)
#
#        cache.delete(cache_key)
#
#        return Response(status=status.HTTP_200_OK)
#
#
#class LoginViewSet(viewsets.ViewSet):
#    def post(self, request):
#        serializer = LoginSerializer(data=request.data)
#        serializer.is_valid(raise_exception=True)
#
#        user = serializer.validated_data['user']
#        refresh = RefreshToken.for_user(user)
#
#        return Response({
#            'refresh': str(refresh),
#            'access': str(refresh.access_token),
#        }, status=status.HTTP_200_OK)
#

class auth(viewsets.ViewSet):
    def post(self):