from rest_framework import viewsets
from .serializers import BrandSerializer, Brand
from rest_framework.permissions import IsAuthenticated


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = 'name'

