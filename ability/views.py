from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotFound
from django.db.models import Q
from .models import Ability, AccessGroup
from .serializers import AbilitySerializer, AccessGroupSerializer

from user.models import BazhayUser


def get_visible_abilities(user):
    return Ability.objects.filter(
        Q(access_type='everyone') |
        Q(author=user) |
        Q(access_type='subscribers', author__subscriptions__user=user) |
        Q(access_type='chosen_ones', chosen_groups__members=user)
    ).distinct()


def can_view_ability(user, ability):
    if ability.access_type == 'everyone':
        return True
    elif ability.access_type == 'only_me' and ability.author == user:
        return True
    elif ability.access_type == 'subscribers' and ability.author.subscriptions.filter(user=user).exists():
        return True
    elif ability.access_type == 'chosen_ones' and ability.chosen_groups.filter(members=user).exists():
        return True
    return False


class AbilityViewSet(viewsets.ModelViewSet):
    serializer_class = AbilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return get_visible_abilities(user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        ability = self.get_object()
        if not can_view_ability(self.request.user, ability):
            raise PermissionDenied("You do not have permission to edit this ability.")
        serializer.save()

    @action(detail=False, methods=['get'])
    def user_abilities(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({'detail': 'Email parameter is required.'}, status=400)

        try:
            user = BazhayUser.objects.get(email=email)
        except BazhayUser.DoesNotExist:
            raise NotFound('User with this email does not exist.')

        abilities = get_visible_abilities(request.user)
        serializer = self.get_serializer(abilities, many=True)
        return Response(serializer.data)


class AccessGroupViewSet(viewsets.ModelViewSet):
    serializer_class = AccessGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = AccessGroup.objects.all()

    def perform_create(self, serializer):
        serializer.save()
