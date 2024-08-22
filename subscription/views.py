from rest_framework import generics
from .serializers import SubscriptionSerializer, Subscription
from permission.permissions import IsRegisteredUser


class SubscribeView(generics.CreateAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsRegisteredUser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SubscriptionListView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsRegisteredUser]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {
            "count": len(response.data),
            "subscriptions": response.data
        }
        return response


class SubscriberListView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsRegisteredUser]

    def get_queryset(self):
        return Subscription.objects.filter(subscribed_to=self.request.user)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {
            "count": len(response.data),
            "subscribers": response.data
        }
        return response
