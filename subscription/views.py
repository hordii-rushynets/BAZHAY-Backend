from rest_framework import generics
from .serializers import SubscriptionSerializer, Subscription
from permission.permissions import IsRegisteredUser
from rest_framework.response import Response
from rest_framework import status


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


class UnsubscribeView(generics.GenericAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsRegisteredUser]

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
