from rest_framework.routers import DefaultRouter
from .views import VideoCutViewSet

router = DefaultRouter()
router.register(r'', VideoCutViewSet, basename='video')

urlpatterns = router.urls
