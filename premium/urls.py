from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import PremiumViewSet, TrialPremiumViewSet

urlpatterns = [
    path('create/', PremiumViewSet.as_view({'post': 'create', 'get': 'list'})),
    path('try/', TrialPremiumViewSet.as_view({'post': 'create'})),
    path('apple-validation/')
]
