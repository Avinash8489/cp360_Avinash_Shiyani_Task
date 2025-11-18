# Libraries
from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken
from apps.user.user_manager import UserManager
from apps.user.constants import UserRoles


class User(AbstractUser):
    # Override Django default fields if needed
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    phone = models.CharField(max_length=20, unique=True)

    # Role
    role = models.CharField(
        max_length=20,
        choices=UserRoles.CHOICES,
        default=UserRoles.END_USER,
    )

    # Extra flags
    is_verified = models.BooleanField(default=False)

    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Manager
    objects = UserManager()

    # Authentication setup
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "phone"]

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def save(self, *args, **kwargs):
        if self.first_name:
            self.first_name = self.first_name.title()

        if self.last_name:
            self.last_name = self.last_name.title()

        super().save(*args, **kwargs)
