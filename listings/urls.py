from django.urls import path
from . import views

urlpatterns = [
    # Categories
    path("categories/", views.category_list_create, name="category-list-create"),
    path("categories/<int:pk>/", views.category_detail, name="category-detail"),

    # Products
    path("products/", views.product_list_create, name="product-list-create"),
    path("products/<slug:slug>/", views.product_detail, name="product-detail"),
    path("products/<slug:slug>/description/", views.product_description, name="product-description"),
    path("products/<slug:slug>/images/", views.product_images, name="product-images"),

    # Product Reviews
    path("products/<slug:slug>/reviews/", views.product_reviews, name="product-reviews"),
    #stock
    path("products/<slug:slug>/stock/", views.update_product_stock, name="product-stock"),
    #variant
    path("products/<slug:slug>/variants/", views.product_variant_list_create, name="product-variants"),
    #wishlist
    path("wishlist/", views.wishlist_view, name="wishlist"),
]
