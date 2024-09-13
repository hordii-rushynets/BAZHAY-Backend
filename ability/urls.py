from rest_framework.routers import DefaultRouter
from .views import WishViewSet, AllWishViewSet, ReservationViewSet, VideoViewSet

router = DefaultRouter()
router.register(r'wishes', WishViewSet, basename='wish')
router.register(r'all-wishes', AllWishViewSet, basename='all_wish')
router.register(r'reservation', ReservationViewSet, basename='reservation')
router.register(r'video', VideoViewSet, basename='video')

urlpatterns = router.urls + []
