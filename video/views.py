from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from .serializers import VideoCutSerializer


class VideoCutViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='cut')
    def cut(self, request):
        serializer = VideoCutSerializer(data=request.data)

        if serializer.is_valid():
            try:
                trimmed_video_base64 = serializer.cut()

                return Response({
                    'trimmed_video': trimmed_video_base64
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
