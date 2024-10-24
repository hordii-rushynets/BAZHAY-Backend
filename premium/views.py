import logging

from rest_framework import viewsets, status, mixins
from rest_framework.request import Request
from rest_framework.response import Response

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


class AppleValidationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):

    def create(self, request, *args, **kwargs):
        services = ApplePayment()
        return Response(services.decryption(request.data.get('signedPayload')), 200)

