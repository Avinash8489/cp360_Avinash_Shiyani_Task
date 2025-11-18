import csv
import io
import logging

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permission import IsAdmin, IsAgent, IsStaff
from apps.user.constants import UserRoles

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

logger = logging.getLogger(__name__)


def log_action(fn):
    def wrapper(self, request, *args, **kwargs):
        user = request.user
        logger.info(
            "products.action",
            extra={
                "user": getattr(user, "email", None),
                "action": fn.__name__,
                "view": self.__class__.__name__,
            },
        )
        return fn(self, request, *args, **kwargs)

    return wrapper

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_deleted=False).select_related("user")
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "restore"}:
            class IsAgentOrStaffOrAdmin(permissions.BasePermission):
                def has_permission(self, request, view):
                    return IsAgent().has_permission(request, view) or \
                           IsStaff().has_permission(request, view) or \
                           IsAdmin().has_permission(request, view)
            return [IsAuthenticated(), IsAgentOrStaffOrAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user, created_by=user, updated_by=user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @log_action
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        instance = self.get_object()
        instance.restore()
        return Response(self.get_serializer(instance).data)

    @action(detail=False, methods=["get"], url_path="export")
    def export(self, request):
        include_products = request.query_params.get("include_products", "false").lower() in {"true", "1", "yes"}
        product_ids = request.query_params.getlist("product_ids")

        qs = self.filter_queryset(self.get_queryset())
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        header = ["category_id", "name", "user_email", "created_at", "updated_at"]
        if include_products:
            header += ["product_id", "product_title", "product_price", "product_status"]
        writer.writerow(header)

        for cat in qs:
            if include_products:
                products = cat.products.filter(is_deleted=False)
                if product_ids:
                    products = products.filter(id__in=product_ids)
                if products.exists():
                    for p in products:
                        writer.writerow([str(cat.category_id), cat.name, cat.user.email, cat.created_at, cat.updated_at, p.id, p.title, str(p.price), p.status])
                else:
                    writer.writerow([str(cat.category_id), cat.name, cat.user.email, cat.created_at, cat.updated_at, "", "", "", ""])
            else:
                writer.writerow([str(cat.category_id), cat.name, cat.user.email, cat.created_at, cat.updated_at])

        resp = HttpResponse(buffer.getvalue(), content_type="text/csv")
        resp["Content-Disposition"] = f"attachment; filename=categories_{timezone.now().date()}.csv"
        return resp


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_deleted=False).select_related("category")
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "restore", "approve", "reject"}:
            class IsAgentOrStaffOrAdmin(permissions.BasePermission):
                def has_permission(self, request, view):
                    return IsAgent().has_permission(request, view) or \
                           IsStaff().has_permission(request, view) or \
                           IsAdmin().has_permission(request, view)
            return [IsAuthenticated(), IsAgentOrStaffOrAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_by=user, updated_by=user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        instance = self.get_object()
        instance.restore()
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        instance = self.get_object()
        if request.user.role not in [UserRoles.STAFF, UserRoles.ADMIN]:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        instance.status = Product.STATUS_SUCCESS
        instance.updated_by = request.user
        instance.save()
        return Response(self.get_serializer(instance).data)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        instance = self.get_object()
        if request.user.role not in [UserRoles.STAFF, UserRoles.ADMIN]:
            return Response({"detail": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        instance.status = Product.STATUS_REJECTED
        instance.updated_by = request.user
        instance.save()
        return Response(self.get_serializer(instance).data)

    @action(detail=False, methods=["get"], url_path="export")
    def export(self, request):
        product_ids = request.query_params.getlist("product_ids")
        qs = self.filter_queryset(self.get_queryset())
        if product_ids:
            qs = qs.filter(id__in=product_ids)

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        header = ["id", "category_id", "title", "description", "price", "status", "created_at", "updated_at"]
        writer.writerow(header)

        for p in qs:
            writer.writerow([p.id, str(p.category.category_id), p.title, p.description, str(p.price), p.status, p.created_at, p.updated_at])

        resp = HttpResponse(buffer.getvalue(), content_type="text/csv")
        resp["Content-Disposition"] = f"attachment; filename=products_{timezone.now().date()}.csv"
        return resp
