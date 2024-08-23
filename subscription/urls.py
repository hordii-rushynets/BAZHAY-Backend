from django.urls import path
from .views import (SubscribeView,
                    UnsubscribeView,
                    SubscriptionListView,
                    SubscriberListView)

urlpatterns = [
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/', UnsubscribeView.as_view(), name='unsubscribe'),

    path('subscriptions/', SubscriptionListView.as_view(), name='subscriptions'),
    path('subscribers/', SubscriberListView.as_view(), name='subscribers'),
]
