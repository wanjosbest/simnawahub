from rest_framework import serializers
from .models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]


class ProductSerializer(serializers.ModelSerializer):
    # ✅ Nested serializer for images
    images = ProductImageSerializer(many=True, read_only=True)
    seller = serializers.StringRelatedField(read_only=True)  # Show seller username

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "price",
            "category",
            "seller",
            "created_at",
            "updated_at",
            "images",
            "stock",
        ]
        read_only_fields = ["slug", "seller", "created_at", "updated_at"]

from .models import ProductReview

class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ProductReview
        fields = ["id", "user", "rating", "comment", "created_at"]


from .models import ProductVariant

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ["id", "product", "name", "price", "stock"]

from .models import Wishlist
class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ["id", "user", "product", "added_at"]
