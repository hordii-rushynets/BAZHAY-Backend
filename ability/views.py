from rest_framework import viewsets, permissions, mixins
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import Serializer
from rest_framework.request import Request

from django.db.models.query import QuerySet
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from .models import Wish, Reservation
from .serializers import WishSerializer, ReservationSerializer, VideoSerializer
from .filters import WishFilter
from .pagination import WishPagination

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
    pagination_class = WishPagination

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
 

class AllWishViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Wish.objects.all()
    serializer_class = WishSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = WishFilter
    pagination_class = WishPagination
    
    def get_queryset(self):
        user = self.request.user
        return Wish.objects.filter(
            Q(access_type='everyone') |
            Q(access_type='only_me', author=user) |
            Q(access_type='subscribers', author__in=Subscription.objects.filter(user=user).values_list('subscribed_to', flat=True)) |
            Q(author=user)
        ).distinct()


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        """Returns the QuerySet of reservation of the requesting user"""
        bazhay_user = self.request.user
        return super().get_queryset().filter(bazhay_user=bazhay_user)


class VideoViewSet(mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    queryset = Wish.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [permissions.IsAuthenticated]

