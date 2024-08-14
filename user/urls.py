from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UpdateUserViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = router.urls + [
    path('update/', UpdateUserViewSet.as_view({'get': 'retrieve', 'put': 'update'})),
]
