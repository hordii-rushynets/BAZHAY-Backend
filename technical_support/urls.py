from rest_framework.routers import DefaultRouter
from .views import TechnicalSupportViewSet

router = DefaultRouter()
router.register(r'', TechnicalSupportViewSet, basename='support')

urlpatterns = router.urls
