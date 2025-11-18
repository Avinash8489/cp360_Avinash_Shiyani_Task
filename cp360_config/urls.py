# Libraries
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


# URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/auth/", include("apps.core.urls")),
    path("api/users/", include("apps.user.urls")),
    path("api/", include("apps.products.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
