from typing import Optional
from rest_framework.request import Request
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

    @action(detail=True, methods=['get'], url_path='wish')
    def paginated_abilities(self, request: Request, slug: Optional[str] = None) -> Response:
        """Returns the paginated wish list of the original brand"""
        brand = self.get_object()
        wish = brand.wishes.all()
        paginator = WishPagination()
        page = paginator.paginate_queryset(wish, request)

        if page is not None:
            serializer = WishSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = WishSerializer(wish, many=True)
        return Response(serializer.data)
