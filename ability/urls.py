from rest_framework.routers import DefaultRouter
from .views import AbilityViewSet

router = DefaultRouter()
router.register(r'', AbilityViewSet, basename='abilities')

urlpatterns = router.urls + []
