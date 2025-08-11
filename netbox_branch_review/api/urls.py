from rest_framework.routers import DefaultRouter
from .views import ChangeRequestViewSet

router = DefaultRouter()
router.register("change-requests", ChangeRequestViewSet, basename="changerequest")
urlpatterns = router.urls