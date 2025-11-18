# Libraries
from django.urls import path

from apps.user.views import (
    AdminUserDetailView,
    AdminUserStatusView,
    LoginView,
    PasswordChangeView,
    ProfileView,
    RegisterView,
)


# URL patterns
urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("login/", LoginView.as_view(), name="user-login"),
    path("profile/", ProfileView.as_view(), name="user-profile"),
    path("profile/password/", PasswordChangeView.as_view(), name="user-password-change"),
    path("admin/users/<int:pk>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("admin/users/<int:pk>/status/", AdminUserStatusView.as_view(), name="admin-user-status"),
]
