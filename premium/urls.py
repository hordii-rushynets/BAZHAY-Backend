from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import PremiumViewSet, TrialPremiumViewSet, AppleValidationViewSet

router = DefaultRouter()
router.register('apple-validation', AppleValidationViewSet, basename='apple_validation')

urlpatterns = router.urls + [
    path('create/', PremiumViewSet.as_view({'post': 'create', 'get': 'list'})),
    path('try/', TrialPremiumViewSet.as_view({'post': 'create'})),
]
