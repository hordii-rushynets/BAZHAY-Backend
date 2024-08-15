from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (AuthViewSet,
                    UpdateUserViewSet,
                    UpdateUserEmailViewSet)


router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'user/update-email', UpdateUserEmailViewSet, basename='update_email')

urlpatterns = router.urls + [
    path('user/', UpdateUserViewSet.as_view({'get': 'retrieve', 'put': 'update'})),
]
