from rest_framework import serializers
from .models import Cart, CartItem
from listings.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=None, write_only=True, source="product")

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "added_at"]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "created_at"]
