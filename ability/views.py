from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotFound
from django.db.models import Q
from .models import Ability
from .serializers import AbilitySerializer

from user.models import BazhayUser

from subscription.models import Subscription


def get_visible_abilities(user):
    return Ability.objects.filter(
        Q(access_type='everyone') |
        Q(author=user) |
        Q(access_type='subscribers', author__subscriptions__user=user)
    ).distinct()


def can_view_ability(user, ability):
    if ability.access_type == 'everyone':
        return True
    elif ability.access_type == 'only_me' and ability.author == user:
        return True
    elif ability.access_type == 'subscribers':
        return Subscription.objects.filter(user=user, subscribed_to=ability.author).exists()
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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        user = request.user
        if not can_view_ability(user, instance):
            return Response({'detail': 'You do not have permission to view this ability.'}, status=403)

        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def user_abilities(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'detail': 'User ID parameter is required.'}, status=400)

        try:
            requested_user = BazhayUser.objects.get(id=user_id)
        except BazhayUser.DoesNotExist:
            raise NotFound('User with this ID does not exist.')

        viewing_user = request.user
        abilities = Ability.objects.filter(author=requested_user)

        visible_abilities = [ability for ability in abilities if can_view_ability(viewing_user, ability)]

        serializer = self.get_serializer(visible_abilities, many=True)
        return Response(serializer.data)
