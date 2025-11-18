
from django.contrib import auth
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from apps.user.constants import UserRoles
from apps.user.models import User
from apps.user.validation import (
    validate_alpha,
    validate_email_format,
    validate_password_strength,
    validate_phone_format,
    validate_role_choice,
    validate_unique_field,
    validate_username_format,
)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "phone",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "role", "is_active", "is_verified", "created_at", "updated_at"]


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "phone",
            "password",
            "first_name",
            "last_name",
            "role",
        ]
        extra_kwargs = {"role": {"required": False}}

    def validate_email(self, value):
        value = validate_email_format(value)
        return validate_unique_field(value, "email", instance=self.instance)

    def validate_username(self, value):
        value = validate_username_format(value)
        return validate_unique_field(value, "username", instance=self.instance)

    def validate_phone(self, value):
        value = validate_phone_format(value)
        return validate_unique_field(value, "phone", instance=self.instance, case_insensitive=False)

    def validate_first_name(self, value):
        return validate_alpha(value, "First name")

    def validate_last_name(self, value):
        return validate_alpha(value, "Last name")

    def validate_role(self, value):
        return validate_role_choice(value)

    def validate_password(self, value):
        validate_password_strength(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise ValidationError({"password": "Password is required."})
        role = validated_data.get("role", UserRoles.END_USER)

        if role == UserRoles.ADMIN:
            user = User.objects.create_superuser(password=password, **validated_data)
        else:
            user = User.objects.create_user(password=password, **validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "phone",
            "first_name",
            "last_name",
            "role",
        ]
        read_only_fields = ["role"]

    def validate_email(self, value):
        value = validate_email_format(value)
        return validate_unique_field(value, "email", instance=self.instance)

    def validate_username(self, value):
        value = validate_username_format(value)
        return validate_unique_field(value, "username", instance=self.instance)

    def validate_phone(self, value):
        value = validate_phone_format(value)
        return validate_unique_field(value, "phone", instance=self.instance, case_insensitive=False)

    def validate_first_name(self, value):
        return validate_alpha(value, "First name")

    def validate_last_name(self, value):
        return validate_alpha(value, "Last name")


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "phone",
            "first_name",
            "last_name",
            "role",
            "is_active",
        ]
        read_only_fields = []

    def validate_email(self, value):
        value = validate_email_format(value)
        return validate_unique_field(value, "email", instance=self.instance)

    def validate_username(self, value):
        value = validate_username_format(value)
        return validate_unique_field(value, "username", instance=self.instance)

    def validate_phone(self, value):
        value = validate_phone_format(value)
        return validate_unique_field(value, "phone", instance=self.instance, case_insensitive=False)

    def validate_first_name(self, value):
        return validate_alpha(value, "First name")

    def validate_last_name(self, value):
        return validate_alpha(value, "Last name")

    def validate_role(self, value):
        return validate_role_choice(value)


class EmailVerificationSerializers(serializers.Serializer):
    token = serializers.CharField(max_length=555)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(write_only=True, min_length=6, max_length=50)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        user = auth.authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid email or password.")
        if not user.is_active:
            raise AuthenticationFailed("Your account is disabled. Contact administrator.")
        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified.")
        attrs["user"] = user
        attrs["tokens"] = user.tokens()
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    new_password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_new_password(self, value):
        return validate_password_strength(value)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["is_active"]