from rest_framework.routers import DefaultRouter
from .views import WishViewSet

router = DefaultRouter()
router.register(r'', WishViewSet, basename='wish')

urlpatterns = router.urls + []
