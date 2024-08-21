from rest_framework.permissions import BasePermission
from .models import Subscription


class IsSubscribedOrOpenAccess(BasePermission):
    """
    A permission that allows access to a resource only if the user is subscribed to the author or if access is
    open to everyone.
    """

    def has_object_permission(self, request, view, obj):
        if obj.access_type == 'everyone':
            return True

        return Subscription.objects.filter(user=request.user, subscribed_to=obj.author).exists()
