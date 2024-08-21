from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsGuestUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_guest


class IsRegisteredUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.is_guest


class IsRegisteredUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.is_guest and request.method in SAFE_METHODS:
            return True

        if not request.user.is_guest:
            return True

        return False