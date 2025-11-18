from typing import Optional

from django.db.models import Q
from rest_framework import serializers

from apps.user.constants import UserRoles
from apps.user.models import User


def validate_alpha(value, field_name):
    if not value.isalpha():
        raise serializers.ValidationError(f"{field_name} must contain only letters.")
    if len(value) > 50:
        raise serializers.ValidationError(f"{field_name} must be ≤ 50 characters.")
    return value


def validate_email_format(value):
    import re
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    if not re.match(pattern, value):
        raise serializers.ValidationError("Invalid email format.")
    return value


def validate_username_format(value):
    import re
    if len(value) > 50:
        raise serializers.ValidationError("Username must be ≤ 50 characters.")
    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9._-]*$", value):
        raise serializers.ValidationError(
            "Username may contain letters, numbers, '.', '-', '_' and cannot start with a special character."
        )
    return value


def validate_phone_format(value):
    if not value.isdigit():
        raise serializers.ValidationError("Phone must contain digits only.")
    if not (8 <= len(value) <= 12):
        raise serializers.ValidationError("Phone must be 8–12 digits.")
    return value


def validate_password_strength(value):
    if not (6 <= len(value) <= 50):
        raise serializers.ValidationError("Password must be 6–50 characters.")
    return value


def validate_unique_field(value, field_name: str, instance: Optional[User] = None, case_insensitive=True):
    lookup = f"{field_name}__iexact" if case_insensitive else field_name
    qs = User.objects.filter(**{lookup: value})
    if instance:
        same_value = getattr(instance, field_name)
        if (same_value.lower() if isinstance(same_value, str) else same_value) == (
            value.lower() if isinstance(value, str) else value
        ):
            return value
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        verbose = field_name.replace("_", " ").title()
        raise serializers.ValidationError(f"{verbose} already exists.")
    return value


def validate_role_choice(value: str) -> str:
    allowed = [choice[0] for choice in UserRoles.CHOICES]
    if value not in allowed:
        raise serializers.ValidationError("Invalid role selection.")
    return value