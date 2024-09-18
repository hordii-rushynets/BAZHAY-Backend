from typing import Optional
from rest_framework.request import Request
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from ability.serializers import WishSerializerForNotUser

from .serializers import BrandSerializer, Brand


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = 'slug'
    pagination_class = PageNumberPagination

    @action(detail=True, methods=['get'], url_path='wish', pagination_class=PageNumberPagination)
    def paginated_abilities(self, request: Request, slug: Optional[str] = None) -> Response:
        """Returns the paginated wish list of the original brand"""
        brand = self.get_object()
        wish = brand.wishes.all()
        serializer = WishSerializerForNotUser(wish, many=True)
        return Response(serializer.data)
