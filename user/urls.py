from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView


from .views import (AuthViewSet,
                    UpdateUserViewSet,
                    UpdateUserEmailViewSet,
                    GuestUserViewSet,
                    UpdateUserPhotoViewSet,
                    GoogleLoginView)


router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'auth/guest', GuestUserViewSet, basename='auth_guest')
router.register(r'user/update-email', UpdateUserEmailViewSet, basename='update_email')

urlpatterns = router.urls + [
    path('user/', UpdateUserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', TokenBlacklistView.as_view(), name='logout'),
    path('user/photo/', UpdateUserPhotoViewSet.as_view({'put': 'update'})),
    path('auth/google/', GoogleLoginView.as_view(), name='google_auth'),
]
