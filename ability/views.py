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
from rest_framework.pagination import PageNumberPagination

from subscription.models import Subscription


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
    """
    ViewSet for managing wishes.

    Provides actions to list, retrieve, create, update, and delete wishes. The view only shows wishes authored by
    the requesting user. It also includes permission checks for creating, updating, and retrieving wishes.

    Attributes:
        queryset (QuerySet): The queryset of `Wish` objects.
        serializer_class (Type[serializers.ModelSerializer]): The serializer used for wish data.
        permission_classes (List[Type[permissions.BasePermission]]): List of permission classes to enforce user authentication.
        filter_backends (Tuple[Type[DjangoFilterBackend]]): Backend filters to apply to the queryset.
        filterset_class (Type[filters.FilterSet]): The filter class to use for filtering the queryset.
        pagination_class (Type[pagination.PageNumberPagination]): The pagination class to use for paginating results.
    """
    queryset = Wish.objects.all()
    serializer_class = WishSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = WishFilter
    pagination_class = PageNumberPagination

    def get_queryset(self) -> QuerySet:
        """
        Returns the QuerySet of wishes authored by the requesting user.

        Filters the queryset to include only wishes created by the currently authenticated user.

        Returns:
            QuerySet: A queryset of `Wish` objects authored by the requesting user.
        """
        user = self.request.user
        return super().get_queryset().filter(author=user)

    def perform_create(self, serializer: Serializer):
        """
        Creates a new wish with the requesting user set as the author.

        Args:
            serializer (Serializer): The serializer instance used to validate and save the wish data.
        """
        serializer.save(author=self.request.user)

    def perform_update(self, serializer: Serializer):
        """
        Updates an existing wish. Checks if the user has permission to edit the wish.

        Args:
            serializer (Serializer): The serializer instance used to validate and save the updated wish data.

        Raises:
            PermissionDenied: If the user does not have permission to edit the wish.
        """
        ability = self.get_object()
        if not can_view_ability(self.request.user, ability):
            raise PermissionDenied("You do not have permission to edit this wish.")
        serializer.save()

    def retrieve(self, request: Request, *args, **kwargs):
        """
        Retrieves a wish by its ID. Checks if the requesting user has permission to view the wish.

        Args:
            request (Request): The HTTP request instance.
            *args: Variable length argument list.
            **kwargs: Keyword arguments containing the ID of the wish to retrieve.

        Returns:
            Response: The HTTP response containing the wish data.

        Raises:
            PermissionDenied: If the user does not have permission to view the wish.
        """
        instance = self.get_object()

        user = request.user
        if not can_view_ability(user, instance):
            return Response({'detail': 'You do not have permission to view this wish.'}, status=403)

        return super().retrieve(request, *args, **kwargs)


class AllWishViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving wishes with filtering and pagination.

    Provides read-only operations to list and retrieve wishes. The queryset is filtered based on access type and
    the user's subscription status. The view also supports pagination and filtering.

    """
    queryset = Wish.objects.all()
    serializer_class = WishSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = WishFilter
    pagination_class = PageNumberPagination

    def get_queryset(self):
        """
        Returns the filtered and paginated QuerySet of wishes.

        Filters the wishes based on access type:
        - `everyone`: Public wishes
        - `only_me`: Wishes authored by the user
        - `subscribers`: Wishes from authors to whom the user is subscribed

        Excludes wishes authored by the requesting user to avoid showing their own wishes.

        Returns:
            QuerySet: A filtered and paginated QuerySet of `Wish` objects.
        """
        user = self.request.user

        queryset = Wish.objects.filter(
            Q(access_type='everyone') |
            Q(access_type='only_me', author=user) |
            Q(access_type='subscribers',
              author__in=Subscription.objects.filter(user=user).values_list('subscribed_to', flat=True))
        )
        return queryset

    def list(self, request, *args, **kwargs):
        self.queryset.exclude(author=self.request.user)
        return super().list(request, *args, **kwargs)


class ReservationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing reservations.

    Provides CRUD operations for reservations where users can create, retrieve, update, and delete their reservations.
    The `get_queryset` method filters reservations to only include those associated with the requesting user.

    Attributes:
        queryset (QuerySet): The queryset of `Reservation` objects.
        serializer_class (Type[serializers.ModelSerializer]): The serializer used for handling reservation data.
        permission_classes (List[Type[permissions.BasePermission]]): List of permission classes to enforce user authentication.
    """
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        """
        Returns the QuerySet of reservations for the requesting user.

        Filters the reservations to include only those that belong to the currently authenticated user.

        Returns:
            QuerySet: A QuerySet of `Reservation` objects associated with the requesting user.
        """
        bazhay_user = self.request.user
        return super().get_queryset().filter(bazhay_user=bazhay_user)


class VideoViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
        ViewSet for updating video associated with a wish.

        Provides the functionality to update video files for the `Wish` model.
        Inherits from `UpdateModelMixin` to handle update operations and
        `GenericViewSet` for standard CRUD operations.

        Attributes:
            queryset (QuerySet): The queryset of `Wish` objects.
            serializer_class (Type[serializers.ModelSerializer]): The serializer used for updating video data.
            permission_classes (List[Type[permissions.BasePermission]]): List of permission classes.
        """
    queryset = Wish.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [permissions.IsAuthenticated]

