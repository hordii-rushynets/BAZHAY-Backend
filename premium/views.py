from rest_framework import viewsets, status, mixins

from .models import Premium
from .serializers import PremiumSerializers, TrialSubscriptionSerializer


class PremiumViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = PremiumSerializers

    def get_queryset(self):
        user = self.request.user
        return Premium.objects.filter(bazhay_user=user)


class TrialPremiumViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = TrialSubscriptionSerializer
