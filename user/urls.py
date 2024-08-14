from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegistrationViewSet, LoginViewSet

router = DefaultRouter()
router.register(r'register', RegistrationViewSet, basename='register')


urlpatterns = router.urls + [
    path('login/', LoginViewSet.as_view({'post': 'post'}))
]
