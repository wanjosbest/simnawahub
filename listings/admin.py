from django.contrib import admin
from .models import (
    Category,
    Product,
    ProductImage,
    ProductReview,
    ProductVariant,
    Wishlist
)

# -----------------------------
# Category
# -----------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


# -----------------------------
# Product
# -----------------------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # number of extra blank images

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "seller", "category", "price", "stock", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "seller__username")
    list_filter = ("category", "created_at")
    inlines = [ProductImageInline, ProductVariantInline]


# -----------------------------
# ProductImage
# -----------------------------
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "image")
    search_fields = ("product__name",)


# -----------------------------
# ProductReview
# -----------------------------
@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user", "rating", "created_at")
    search_fields = ("product__name", "user__username")
    list_filter = ("rating", "created_at")


# -----------------------------
# ProductVariant
# -----------------------------
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "name", "price", "stock")
    search_fields = ("product__name", "name")


# -----------------------------
# Wishlist
# -----------------------------
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "added_at")
    search_fields = ("user__username", "product__name")
    list_filter = ("added_at",)
