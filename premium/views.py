import logging

from rest_framework import viewsets, status, mixins
from rest_framework.request import Request

from .models import Premium
from .serializers import PremiumSerializers, TrialSubscriptionSerializer
from .services import ApplePayment


class PremiumViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PremiumSerializers

    def get_queryset(self):
        user = self.request.user
        return Premium.objects.filter(bazhay_user=user)


class TrialPremiumViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = TrialSubscriptionSerializer


class AppleValidation(viewsets.ViewSet):
    def post(self, request: Request):
        services = ApplePayment()

        return services.decryption(request.data.get(''))

