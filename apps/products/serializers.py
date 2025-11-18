from rest_framework import serializers
from .models import Category, Product, ProductVideo
from apps.user.constants import UserRoles


class ProductVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVideo
        fields = ["id", "file", "uploaded_at"]
        read_only_fields = ["uploaded_at"]

    def validate_file(self, value):
        # individual file size limit: not strictly required, but checking
        max_single_mb = 20
        if value.size > max_single_mb * 1024 * 1024:
            raise serializers.ValidationError("Single video must be <= 20 MB")
        return value


class ProductSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    videos = ProductVideoSerializer(many=True, required=False, read_only=True)
    # allow uploading video files on create/update (separately handled)
    video_files = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "title",
            "description",
            "price",
            "status",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "videos",
            "video_files",
            "is_deleted",
        ]
        read_only_fields = ["created_at", "updated_at", "created_by", "updated_by", "videos", "is_deleted"]

    def get_created_by(self, obj):
        return getattr(obj.created_by, "email", None)

    def get_updated_by(self, obj):
        return getattr(obj.updated_by, "email", None)

    def validate_title(self, value):
        if len(value) > 50:
            raise serializers.ValidationError("Title must be <= 50 characters")
        return value

    def validate_description(self, value):
        if len(value) > 251:
            raise serializers.ValidationError("Description must be <= 251 characters")
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be >= 0")
        return value

    def validate_status(self, value):
        allowed = [st[0] for st in Product.STATUS_CHOICES]
        if value not in allowed:
            raise serializers.ValidationError(f"Invalid status. Allowed: {allowed}")
        return value

    def validate(self, attrs):
        # check total video size if video_files provided
        video_files = attrs.get("video_files", [])
        if self.instance:
            # existing product
            existing_size = sum([v.file.size for v in self.instance.videos.all() if v.file and hasattr(v.file, "size")])
        else:
            existing_size = 0

        new_total = existing_size + sum([f.size for f in video_files])
        if new_total > 20 * 1024 * 1024:
            raise serializers.ValidationError("Total videos size for this product must be <= 20 MB")
        return attrs

    def create(self, validated_data):
        video_files = validated_data.pop("video_files", [])
        request = self.context.get("request")
        user = getattr(request, "user", None)
        product = Product.objects.create(**validated_data)
        if user:
            product.created_by = user
            product.updated_by = user
            product.save()
        
        for f in video_files:
            pv = ProductVideo.objects.create(product=product, file=f)
            from apps.products.tasks import process_uploaded_video
            process_uploaded_video.delay(pv.id)
        
        return product

    def update(self, instance, validated_data):
        video_files = validated_data.pop("video_files", [])
        request = self.context.get("request")
        user = getattr(request, "user", None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        if user:
            instance.updated_by = user
        instance.save()
        
        for f in video_files:
            pv = ProductVideo.objects.create(product=instance, file=f)
            from apps.products.tasks import process_uploaded_video
            process_uploaded_video.delay(pv.id)
        
        return instance


class CategorySerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["category_id", "name", "user", "created_at", "updated_at", "created_by", "updated_by", "products_count", "is_deleted"]
        read_only_fields = ["category_id", "created_at", "updated_at", "created_by", "updated_by", "products_count", "is_deleted"]

    def get_created_by(self, obj):
        return getattr(obj.created_by, "email", None)

    def get_updated_by(self, obj):
        return getattr(obj.updated_by, "email", None)

    def get_products_count(self, obj):
        return obj.products.filter(is_deleted=False).count()

    def validate_name(self, value):
        if len(value) > 50:
            raise serializers.ValidationError("Name must be <= 50 characters")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        # set user (owner) from token request user
        if user and user.is_authenticated:
            validated_data["user"] = user
            validated_data["created_by"] = user
            validated_data["updated_by"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            instance.updated_by = user
        return super().update(instance, validated_data)
