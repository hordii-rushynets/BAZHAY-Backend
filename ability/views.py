from rest_framework import viewsets
from rest_framework.response import Response
from .serializers import AbilitySerializer, Ability
from rest_framework.permissions import IsAuthenticated


class AbilityViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Ability.objects.all()
    serializer_class = AbilitySerializer
