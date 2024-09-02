from rest_framework.routers import DefaultRouter
from .views import WishViewSet, ReservationViewSet

router = DefaultRouter()
router.register(r'wishes', WishViewSet, basename='wishes')
router.register(r'reservation', ReservationViewSet, basename='reservation')

urlpatterns = router.urls + []
