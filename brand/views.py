from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from ability.pagination import WishPagination
from ability.serializers import WishSerializer

from .serializers import BrandSerializer, Brand


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = 'slug'

    @action(detail=True, methods=['get'], url_path='abilities')
    def paginated_abilities(self, request, slug=None):
        brand = self.get_object()
        abilities = brand.abilities.all()
        paginator = WishPagination()
        page = paginator.paginate_queryset(abilities, request)

        if page is not None:
            serializer = WishSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = WishSerializer(abilities, many=True)
        return Response(serializer.data)
