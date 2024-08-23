from rest_framework.routers import DefaultRouter
from .views import AbilityViewSet, AccessGroupViewSet

router = DefaultRouter()
router.register(r'abilities', AbilityViewSet, basename='abilities')
router.register(r'access-groups', AccessGroupViewSet, 'access_groups')

urlpatterns = router.urls + []
