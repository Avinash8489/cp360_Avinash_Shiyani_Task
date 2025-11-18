from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.products.views import CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")

urlpatterns = router.urls
