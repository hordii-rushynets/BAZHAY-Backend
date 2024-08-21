from rest_framework import viewsets
from rest_framework.response import Response
from .models import Ability
from .serializers import AbilitySerializer
from .permissions import IsSubscribedOrOpenAccess
from rest_framework.permissions import IsAuthenticated


class AbilityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AbilitySerializer
    permission_classes = [IsSubscribedOrOpenAccess, IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            queryset = Ability.objects.filter(author=user)
            return queryset
        else:
            return Ability.objects.none()

    def retrieve(self, request, *args, **kwargs):
        ability = self.get_object()
        self.check_object_permissions(request, ability)
        serializer = self.get_serializer(ability)
        return Response(serializer.data)

