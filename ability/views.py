from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.serializers import Serializer
from rest_framework.request import Request

from django.db.models.query import QuerySet
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from .models import Wish
from .serializers import WishSerializer
from .filters import WishFilter

from user.models import BazhayUser

from subscription.models import Subscription


def get_visible_abilities(user):
    """Checks access to the wish"""
    return Wish.objects.filter(
        Q(access_type='everyone') |
        Q(author=user) |
        Q(access_type='subscribers', author__subscriptions__user=user)
    ).distinct()


def can_view_ability(user, ability):
    """Checks access to the wish"""
    if ability.access_type == 'everyone':
        return True
    elif ability.access_type == 'only_me' and ability.author == user:
        return True
    elif ability.access_type == 'subscribers':
        return Subscription.objects.filter(user=user, subscribed_to=ability.author).exists() or ability.author == user
    return False


class WishViewSet(viewsets.ModelViewSet):
    """Wish view set"""
    queryset = Wish.objects.all()
    serializer_class = WishSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = WishFilter

    def get_queryset(self) -> QuerySet:
        """Returns the QuerySet of wish of the requesting user"""
        user = self.request.user
        return super().get_queryset().filter(author=user)

    def perform_create(self, serializer: Serializer):
        """Creates wish"""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer: Serializer):
        """Update wish"""
        ability = self.get_object()
        if not can_view_ability(self.request.user, ability):
            raise PermissionDenied("You do not have permission to edit this ability.")
        serializer.save()

    def retrieve(self, request: Request, *args, **kwargs):
        """Returns a wish by id"""
        instance = self.get_object()

        user = request.user
        if not can_view_ability(user, instance):
            return Response({'detail': 'You do not have permission to view this ability.'}, status=403)

        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def user_wish(self, request: Request) -> Response:
        """Returns all user wish by id"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'detail': 'User ID parameter is required.'}, status=400)

        try:
            requested_user = BazhayUser.objects.get(id=user_id)
        except BazhayUser.DoesNotExist:
            raise NotFound('User with this ID does not exist.')

        viewing_user = request.user
        abilities = Wish.objects.filter(author=requested_user)

        visible_abilities = [ability for ability in abilities if can_view_ability(viewing_user, ability)]

        serializer = self.get_serializer(visible_abilities, many=True)
        return Response(serializer.data)
