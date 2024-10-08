from django.core.cache import cache
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from .models import BazhayUser, Address, PostAddress
from .authentication import IgnoreInvalidTokenAuthentication
from .serializers import (CreateUserSerializer,
                          ConfirmCodeSerializer,
                          UpdateUserSerializers,
                          EmailUpdateSerializer,
                          EmailConfirmSerializer,
                          GuestUserSerializer,
                          ConvertGuestUserSerializer,
                          UpdateUserPhotoSerializer,
                          GoogleAuthSerializer,
                          ReturnBazhayUserSerializer,
                          AddressSerializer,
                          PostAddressSerializer)
from .utils import save_and_send_confirmation_code
from .filters import BazhayUserFilter

from permission.permissions import (IsRegisteredUser,
                                    IsRegisteredUserOrReadOnly,
                                    IsOwner)


def is_valid(serializer: serializers.Serializer) -> Response:
    """
    Validates and processes data using the provided serializer.

    If the serializer data is valid, the method saves the data and sends a confirmation code.
    Returns an HTTP response indicating the result of the validation.

    Args:
        serializer (serializers.Serializer): The serializer instance containing the data to be validated.

    Returns:
        Response: HTTP response with status 200 OK if valid, or 400 Bad Request with errors if invalid.
    """
    if serializer.is_valid():
        user = serializer.save()
        save_and_send_confirmation_code(user.email)
        return Response(status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthViewSet(viewsets.ViewSet):
    """
    ViewSet for handling user authentication tasks such as registration, login,
    and transforming guest users into standard users.

    Provides endpoints for user registration, logging in, and converting guest users.
    Additionally, it includes a confirmation endpoint to verify codes and complete user registration or conversion.

    Methods:
        create(request: Request) -> Response:
            Handles user registration, login, or conversion of a guest user to a standard user.

        confirm_code(request: Request) -> Response:
            Validates the confirmation code, completes the user registration or conversion,
            and returns JWT tokens along with the registration status.
    """
    authentication_classes = [IgnoreInvalidTokenAuthentication]
    permission_classes = [AllowAny]

    def create(self, request: Request) -> Response:
        """
        Handles registration, login, or transformation of a guest user into a standard user.

        If the user is authenticated and is a guest, converts them to a standard user.
        Otherwise, processes registration or login for a new user.

        Args:
            request (Request): The incoming request containing user data.

        Returns:
            Response: HTTP response with status 200 OK if successful, or 400 Bad Request with errors if validation fails.
        """
        if request.user.is_authenticated and request.user.is_guest:
            serializer = ConvertGuestUserSerializer(data=request.data, instance=request.user)
            return is_valid(serializer)
        else:
            serializer = CreateUserSerializer(data=request.data)
            return is_valid(serializer)

    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm_code(self, request: Request) -> Response:
        """
        Validates the confirmation code and completes the user registration or conversion process.

        If the user is a guest, it converts them to a standard user. Deletes the confirmation code from cache,
        generates JWT tokens, and returns user registration status along with the tokens.

        Args:
            request (Request): The incoming request containing the confirmation code.

        Returns:
            Response: HTTP response with status 200 OK if the confirmation is successful and user is registered,
                      or 201 Created if the user is newly registered, or 400 Bad Request with errors if validation fails.
        """
        serializer = ConfirmCodeSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            if user.is_guest:
                serializer = ConvertGuestUserSerializer(instance=user, data={'email': user.email})
                if serializer.is_valid():
                    serializer.save()

            cache.delete(f"code_{user.email}")

            refresh = RefreshToken.for_user(user)
            is_already_registered = user.is_already_registered
            data = {
                'is_already_registered': is_already_registered,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            status_code = status.HTTP_200_OK if is_already_registered else status.HTTP_201_CREATED
            return Response(data, status=status_code)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserViewSet(viewsets.GenericViewSet,
                        mixins.UpdateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin):
    """
    ViewSet for retrieving, updating, and deleting the currently authenticated user.

    Provides functionality to update or retrieve user details, and delete the user.
    Access is controlled to ensure only the authenticated user can update or delete their own data.

    Methods:
        get_object():
            Returns the user object that matches the current authenticated user's ID.
    """
    queryset = BazhayUser.objects.all()
    serializer_class = UpdateUserSerializers
    permission_classes = [IsRegisteredUserOrReadOnly]

    def get_object(self):
        """
        Returns the user object that corresponds to the current authenticated user's ID.

        Returns:
            BazhayUser: The user instance associated with the authenticated user.
        """
        return self.queryset.filter(id=self.request.user.id).first()


class UpdateUserEmailViewSet(viewsets.ViewSet):
    """
    ViewSet for updating the user's email address and confirming the email change.

    Provides actions for requesting an email change and confirming the change via a confirmation code.

    Methods:
        create(request: Request) -> Response:
            Initiates an email change request by validating the new email and sending a confirmation code.

        confirm_code(request: Request) -> Response:
            Confirms the email change by validating the confirmation code and updating the user's email.
    """
    permission_classes = [IsRegisteredUser]

    def create(self, request: Request) -> Response:
        """
        Requests an email change by validating the new email and sending a confirmation code.

        Args:
            request (Request): The incoming request containing the new email address.

        Returns:
            Response: A response with status 200 if the email change request is successful,
                      or status 400 with validation errors if the request fails.
        """
        serializer = EmailUpdateSerializer(data=request.data)
        user = request.user

        if serializer.is_valid():
            new_email = serializer.validated_data['email']
            cache.set(f"pending_email_change_{user.id}", new_email, timeout=3600)
            save_and_send_confirmation_code(new_email)
            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm_code(self, request: Request) -> Response:
        """
        Confirms the email change by validating the confirmation code and updating the user's email.

        Args:
            request (Request): The incoming request containing the confirmation code.

        Returns:
            Response: A response with status 200 if the confirmation is successful,
                      or status 400 with validation errors if the confirmation fails.
        """
        user = request.user
        serializer = EmailConfirmSerializer(data=request.data, user=user)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GuestUserViewSet(viewsets.ViewSet):
    """
    ViewSet for creating and logging in guest users.

    This viewset handles the creation of guest users and provides JWT tokens for authentication.
    It uses custom authentication and permission classes to allow access without standard token validation.

    Methods:
        create(request: Request) -> Response:
            Handles the creation of a guest user and returns JWT tokens if successful.
            Returns a 201 status code on successful creation, or a 400 status code with errors if validation fails.
    """
    authentication_classes = [IgnoreInvalidTokenAuthentication]
    permission_classes = [AllowAny]

    def create(self, request: Request) -> Response:
        """
        Creates a guest user and returns JWT tokens for authentication.

        Args:
            request (Request): The incoming request containing the guest user data.

        Returns:
            Response: A response containing refresh and access tokens if the user is successfully created,
                      or validation errors if the creation fails.
        """
        serializer = GuestUserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserPhotoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for updating the user's profile photo.

    Provides endpoints for updating the photo of the currently authenticated user.
    The viewset ensures that only the authenticated user can update their own photo.

    Methods:
        get_object():
            Returns the object (user) that matches the current authenticated user's ID.
    """
    queryset = BazhayUser.objects.all()
    serializer_class = UpdateUserPhotoSerializer
    permission_classes = [IsRegisteredUserOrReadOnly]

    def get_object(self):
        """
        Returns the user object that corresponds to the current authenticated user's ID.

        Returns:
            BazhayUser: The user instance associated with the authenticated user.
        """
        return self.queryset.filter(id=self.request.user.id).first()


class GoogleLoginView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ViewSet for handling Google authorization and user login.

    This viewset processes Google OAuth2 tokens, creates or retrieves a user based on the token,
    and returns JWT tokens for authenticated access.

    Methods:
        create(request: Request, *args, **kwargs) -> Response:
            Validates the Google authentication token, creates or retrieves a user,
            and returns access and refresh tokens for the user.
    """
    serializer_class = GoogleAuthSerializer

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Handles the creation of a user based on the Google OAuth2 token and returns JWT tokens.

        Args:
            request (Request): The incoming request containing the Google token.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A response containing access and refresh tokens if the token is valid.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        data = {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
        return Response(data, status=status.HTTP_200_OK)


class ListUserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing and retrieving user details.

    Provides read-only operations for listing all users and retrieving individual user details.
    Applies authentication, pagination, and filtering to the user list.

    Methods:
        get_serializer_class():
            Returns the appropriate serializer class based on the action being performed.

        get_queryset():
            Excludes the current authenticated user from the queryset.
    """
    serializer_class = ReturnBazhayUserSerializer
    queryset = BazhayUser.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = BazhayUserFilter

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the action being performed.

        For 'list' action, returns ReturnBazhayUserSerializer.
        For 'retrieve' action, returns UpdateUserSerializers.

        Returns:
            Serializer: The serializer class for the current action.
        """
        serializers = {
            'list': ReturnBazhayUserSerializer,
            'retrieve': UpdateUserSerializers
        }

        return serializers.get(self.action, ReturnBazhayUserSerializer)

    def get_queryset(self):
        """
        Returns the queryset of users excluding the current authenticated user.

        Returns:
            QuerySet: The filtered queryset of users.
        """
        return self.queryset.exclude(id=self.request.user.id)


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PostAddressViewSet(viewsets.ModelViewSet):
    queryset = PostAddress.objects.all()
    serializer_class = PostAddressSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return PostAddress.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

