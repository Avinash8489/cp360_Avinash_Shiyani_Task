import uuid

from django.conf import settings
from django.db import models

from apps.core.models import SoftDeleteModel, TimestampedModel


class Category(TimestampedModel, SoftDeleteModel):
    category_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="categories", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def soft_delete(self):
        # soft delete products under this category as well
        for p in self.products.filter(is_deleted=False):
            p.soft_delete()
        super().soft_delete()

    def hard_delete(self):
        # hard delete products first
        for p in self.products.all():
            p.hard_delete()
        return super().hard_delete()


class Product(TimestampedModel, SoftDeleteModel):
    STATUS_UPLOADED = "uploaded"
    STATUS_REJECTED = "rejected"
    STATUS_SUCCESS = "success"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_UPLOADED, "Uploaded"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=251, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_UPLOADED)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def total_video_size_mb(self):
        total = 0
        for v in self.videos.all():
            if v.file and hasattr(v.file, "size"):
                total += v.file.size
        return round(total / (1024 * 1024), 3)


def product_video_upload_to(instance, filename):
    return f"products/{instance.product.id}/videos/{filename}"


class ProductVideo(SoftDeleteModel):
    product = models.ForeignKey(Product, related_name="videos", on_delete=models.CASCADE)
    file = models.FileField(upload_to=product_video_upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def soft_delete(self):
        super().soft_delete()
