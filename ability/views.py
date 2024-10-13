from rest_framework import viewsets, permissions, mixins
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import Serializer
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from django.core.cache import cache
from django.db.models.query import QuerySet
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend

from .models import Wish, Reservation, CandidatesForReservation
from .serializers import (WishSerializer,
                          ReservationSerializer,
                          VideoSerializer,
                          CombinedSearchSerializer,
                          QuerySerializer)

from .filters import WishFilter, ReservationFilter
from .services import PopularRequestService

from subscription.models import Subscription
from user.models import BazhayUser
from brand.models import Brand
from permission.permissions import IsRegisteredUser, IsPremium


SECONDS_IN_A_DAY = 86400


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
        self.queryset.exclude(author=self.request.user).order_by('-views_number')
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def view(self, request, pk=None):
        wish = self.get_object()

        if wish.author == request.user:
            return Response({'message': 'You cannot view your own wish.'}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"user:{request.user.id}:viewed_wish:{wish.id}"

        if cache.get(cache_key):
            return Response(status=status.HTTP_200_OK)

        cache.set(cache_key, True, timeout=7 * SECONDS_IN_A_DAY)

        wish.views_number += 1
        wish.save()

        return Response(status=status.HTTP_200_OK)


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


class SearchView(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    View for searching across BazhayUser, Wish, and Brand models.
    """
    serializer_class = CombinedSearchSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    service = PopularRequestService()

    def list(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle GET requests to search across users and wishes

        :param request: DRF request object containing search query.
        :return: Response with serialized search results or an error message if no query is provided.
        """
        query = request.query_params.get('query', None)

        if query:
            querysets = self.get_queryset(query)
            self.service.set(query)

            self.__delete_not_using_fields(request, querysets)

            active_fields = len(querysets)

            if active_fields == 3:
                self.__querysets_trim(querysets, 5)
            elif active_fields == 2:
                self.__querysets_trim(querysets, 8)
            elif active_fields == 1:
                return self.__pagination_one_field(request, querysets)

            serializer = self.get_serializer(querysets, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"detail": "No query provided."}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self, query: str) -> dict:
        """
        Retrieve querysets based on the search query from the BazhayUser, Wish and Brand models.

        :param query: The search term.

        :return: A dictionary containing querysets for both users and wishes filtered by the search term.
        """
        return {
            'users': self.__get_bazhay_user_results(query),
            'wishes': self.__get_wish_results(query),
            'brands': self.__get_brand_results(query),
        }

    def __querysets_trim(self, queryset: dict, size: int) -> None:
        """
        Trims the query to the required length in each key-value pair.

        :param queryset (dict): Dictionary where the key is a string and the value is a list.
        :param size (int): The size to which you want to trim.
        :return: None.
        """
        for key in queryset.keys():
            queryset[key] = queryset[key][:size]

    def __get_bazhay_user_results(self, query: str | None) -> tuple[BazhayUser]:
        """
        Returns a tuple of users.

        :param query (str): Search query.
        :return: The tuple BazhayUser.
        """
        return BazhayUser.objects.filter(
            Q(email__icontains=query)
            | Q(username__icontains=query)
            | Q(about_user__icontains=query)).exclude(email=self.request.user.email).exclude(is_superuser=True
            ).annotate(subscriber_count=Count('subscribers')).order_by('-subscriber_count')

    def __get_wish_results(self, query: str | None) -> tuple[Wish]:
        """
        Returns a tuple of wishes.

        :param query (str): Search query.
        :return: The tuple Wish.
        """
        return Wish.objects.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(additional_description__icontains=query)
            | Q(author__username__icontains=query)
            | Q(brand_author__name__icontains=query)
            | Q(brand_author__nickname__icontains=query)
            | Q(news_author__title__icontains=query)
            | Q(news_author__description__icontains=query)
        ).exclude(author=self.request.user).order_by('-views_number')

    def __get_brand_results(self, query: str | None) -> tuple[Brand]:
        """
        Returns a tuple of brands.

        :param query (str): Search query.
        :return: The tuple Brand.
        """
        return Brand.objects.filter(Q(name__icontains=query)
                  | Q(name__icontains=query)
                  | Q(nickname__icontains=query)
                  | Q(description__icontains=query)).order_by('-views_number')

    def __delete_not_using_fields(self, request: Request, queryset: dict) -> None:
        """
        Removes unnecessary fields from queryset. Changes the one that was transmitted.

        :param request (Request): For information about the required fields.
        :param queryset (Queryset): Queryset that will be changed in the workflow.
        :return: None.
        """
        users = request.query_params.get('users', 'true').lower() == 'false'
        wishes = request.query_params.get('wishes', 'true').lower() == 'false'
        brands = request.query_params.get('brands', 'true').lower() == 'false'

        if users:
            del queryset['users']
        if wishes:
            del queryset['wishes']
        if brands:
            del queryset['brands']

    def __pagination_one_field(self, request: Request, queryset: dict) -> Response:
        """
        Returns the paginated page.

        :param request (Request): Transferred to the serializer.
        :paraam queryset (dict): data to be paginated.

        :return: paginated Response
        """
        key = next(iter(queryset))
        paginated_queryset = self.paginate_queryset(queryset[key])

        if paginated_queryset is not None:
            serializer = self.get_serializer({key: paginated_queryset}, context={'request': request})
            return self.get_paginated_response(serializer.data)


class QueryView(viewsets.mixins.CreateModelMixin, viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Add and return popular queries.
    """

    serializer_class = QuerySerializer
    service = PopularRequestService()

    def get_queryset(self):
        """
        Returns a list of queries matching the input parameter.

        :return: List of dictionaries containing 'query' and 'count' keys.
        """
        query = self.request.query_params.get('query', None)
        results = self.service.get(query)

        return [{'query': result['query'], 'count': result['count']} for result in results]

    def create(self, request):
        """
        Saves a new query to the service.

        :param request (Request): Request object with query data.
        :return: Response indicating the result of the operation.
        """
        query = request.data.get('query')
        if not query:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        self.service.set(query)
        return Response({'message': 'Query saved successfully'}, status=status.HTTP_201_CREATED)


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated, IsRegisteredUser]
    filter_backends = (DjangoFilterBackend, )
    filterset_class = ReservationFilter

    def get_queryset(self):
        return self.queryset.filter(wish__author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        if not request.user.is_premium():
            raise permissions.PermissionDenied('Access restricted to premium users only.')

        return super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        if not request.user.is_premium():
            raise permissions.PermissionDenied('Access restricted to premium users only.')

        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsRegisteredUser, IsPremium])
    def select_user(self, request, pk=None):
        reservation = self.get_object()

        candidate_id = request.data.get('candidate_id')
        try:
            candidate = CandidatesForReservation.objects.get(bazhay_user=candidate_id, reservation=reservation)
        except CandidatesForReservation.DoesNotExist:
            return Response({'detail': 'Candidate not found.'}, status=status.HTTP_404_NOT_FOUND)

        reservation.selected_user = candidate.bazhay_user
        reservation.save()

        return Response({'detail': 'Candidate selected successfully.'}, status=status.HTTP_200_OK)

