from typing import Optional
from rest_framework.request import Request
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from ability.pagination import WishPagination
from ability.serializers import WishSerializer

from .serializers import NewsSerializers, News


class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = News.objects.all().order_by('-priority')  # Sort by priority (from highest to lowest)
    serializer_class = NewsSerializers
    lookup_field = 'slug'

    @action(detail=True, methods=['get'], url_path='wish')
    def paginated_abilities(self, request: Request, slug: Optional[str] = None) -> Response:
        """Returns the paginated wish list of the original brand"""
        news = self.get_object()
        wish = news.wishes.all()
        paginator = WishPagination()
        page = paginator.paginate_queryset(wish, request)

        if page is not None:
            serializer = WishSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = WishSerializer(wish, many=True)
        return Response(serializer.data)
