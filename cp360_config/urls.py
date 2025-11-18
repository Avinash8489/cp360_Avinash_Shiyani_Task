# Libraries
from django.contrib import admin
from django.urls import path, include   


# URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/auth/", include("apps.core.urls")),
    path("api/users/", include("apps.user.urls")),
    # path("api/products/", include("apps.product.urls")),
]
