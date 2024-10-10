from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsGuestUser(BasePermission):
    """Provides a toast to a guest user """
    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated and request.user.is_guest


class IsRegisteredUser(BasePermission):
    """Grant access to a regular user, deny access to a guest """
    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated and not request.user.is_guest


class IsRegisteredUserOrReadOnly(BasePermission):
    """Give full access to a regular user, if a guest user, then only for reading """
    def has_permission(self, request, view) -> bool:
        if not request.user.is_authenticated:
            return False

        if request.user.is_guest and request.method in SAFE_METHODS:
            return True

        if not request.user.is_guest:
            return True

        return False


class IsOwner(BasePermission):
    """
    Allows access only to the author (owner) of the record.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsPremium(BasePermission):
    """
    Access only for premium users.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            try:
                premium = request.user.premium
                return premium.is_active
            except:
                return False
        return False
