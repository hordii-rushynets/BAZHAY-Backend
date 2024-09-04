from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import WishViewSet, AllWishViewSet, WishShareView

router = DefaultRouter()
router.register(r'wishes', WishViewSet, basename='wish')
router.register(r'all-wishes', AllWishViewSet, basename='all_wish')

urlpatterns = router.urls + [
    path('wishes/<int:pk>/share/', WishShareView.as_view(), name='wish-share'),
]
