from rest_framework import viewsets
from rest_framework.viewsets import mixins
from rest_framework.permissions import IsAuthenticated

from .serializers import TechnicalSupportSerializer
from .models import TechnicalSupport

from permission.permissions import IsRegisteredUser


class TechnicalSupportViewSet(mixins.CreateModelMixin,
                              mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    queryset = TechnicalSupport.objects.all()
    serializer_class = TechnicalSupportSerializer
    permission_classes = [IsAuthenticated, IsRegisteredUser]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
