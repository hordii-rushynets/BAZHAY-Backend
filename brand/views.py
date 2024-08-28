from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from ability.pagination import AbilityPagination
from ability.serializers import AbilitySerializer

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
        paginator = AbilityPagination()
        page = paginator.paginate_queryset(abilities, request)

        if page is not None:
            serializer = AbilitySerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = AbilitySerializer(abilities, many=True)
        return Response(serializer.data)
