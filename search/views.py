from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CombinedSearchSerializer


class SearchView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', None)

        if query:
            serializer = CombinedSearchSerializer(data={'query': query})
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_200_OK)

