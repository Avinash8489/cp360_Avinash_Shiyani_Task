from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from apps.user.constants import UserRoles
from apps.user.models import User
from apps.user.serializers import (
    AdminUserUpdateSerializer,
    PasswordChangeSerializer,
    RegisterUserSerializer,
    UserDetailSerializer,
    UserLoginSerializer,
    UserStatusSerializer,
    UserUpdateSerializer,
)


def _is_admin(user: User) -> bool:
    if not user or not user.is_authenticated:
        return False
    return user.is_staff or user.role == UserRoles.ADMIN or user.is_superuser


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterUserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        requested_role = data.get("role", UserRoles.END_USER)

        if requested_role == UserRoles.ADMIN and not _is_admin(request.user):
            return Response(
                {"detail": "Only admin users can create another admin."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not request.user.is_authenticated:
            data["role"] = UserRoles.END_USER

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "User registered successfully.",
                "data": UserDetailSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": "Invalid credentials.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        validated = serializer.validated_data
        user = validated["user"]
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        return Response(
            {
                "message": f"Login successful. Welcome {user.username}.",
                "data": UserDetailSerializer(user).data,
                "tokens": validated["tokens"],
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return Response(UserDetailSerializer(request.user).data)

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Profile updated successfully.", "data": UserDetailSerializer(request.user).data}
        )


class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password updated successfully."})


class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = AdminUserUpdateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        if user.role == UserRoles.ADMIN and user.pk != request.user.pk:
            return Response(
                {"detail": "You cannot modify another admin user."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)


class AdminUserStatusView(generics.UpdateAPIView):
    serializer_class = UserStatusSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        if user.role == UserRoles.ADMIN and user.pk != request.user.pk:
            return Response(
                {"detail": "You cannot deactivate another admin user."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, **kwargs)
