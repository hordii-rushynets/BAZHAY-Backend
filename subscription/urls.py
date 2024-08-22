from django.urls import path
from .views import SubscribeView, SubscriptionListView, SubscriberListView

urlpatterns = [
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('subscriptions/', SubscriptionListView.as_view(), name='subscriptions'),
    path('subscribers/', SubscriberListView.as_view(), name='subscribers'),
]
