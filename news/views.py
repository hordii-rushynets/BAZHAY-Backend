from typing import Optional
from rest_framework.request import Request
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from ability.serializers import WishSerializerForNotUser

from .serializers import NewsSerializers, News


class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = News.objects.all().order_by('-priority')  # Sort by priority (from highest to lowest)
    serializer_class = NewsSerializers
    lookup_field = 'slug'
    pagination_class = PageNumberPagination

    @action(detail=True, methods=['get'], url_path='wish')
    def wishes(self, request: Request, slug: Optional[str] = None) -> Response:
        """Returns the paginated wish list of the original brand"""
        news = self.get_object()
        wish = news.wishes.all()

        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(wish, request)

        serializer = WishSerializerForNotUser(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
