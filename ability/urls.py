from rest_framework.routers import DefaultRouter
from .views import WishViewSet, AllWishViewSet

router = DefaultRouter()
router.register(r'wishes', WishViewSet, basename='wish')
router.register(r'all-wishes', AllWishViewSet, basename='all_wish')

urlpatterns = router.urls + []
