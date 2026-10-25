from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import BookingViewSet, EquipmentViewSet, bookings_page

router = SimpleRouter()
router.register("equipment", EquipmentViewSet, basename="equipment")
router.register("bookings", BookingViewSet, basename="bookings")

urlpatterns = [
    path("bookings/", bookings_page, name="bookings_page"),
    path("api/", include(router.urls)),
]

