import logging

from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from .serializers import GoogleValidateSerializer
from .models import Premium
from .services import ApplePayment

from permission.permissions import IsRegisteredUser


class AppleValidationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):

    def create(self, request, *args, **kwargs):
        services = ApplePayment()
        return Response(services.decryption(request.data.get('signedPayload')), 200)


class GoogleValidationViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsRegisteredUser]
    serializer_class = GoogleValidateSerializer

    def get_queryset(self):
        return Premium.objects.filter(bazhay_user=self.request.user)

