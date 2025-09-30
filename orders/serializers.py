from rest_framework import serializers
from .models import Order, OrderItem,Payment,ShippingAddress
from listings.serializers import ProductSerializer


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ["id", "user", "order", "address", "city", "postal_code", "country", "created_at"]
        read_only_fields = ["user", "order", "created_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = ShippingAddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "status", "total_price", "created_at", "updated_at", "items"," shipping_address"]
        read_only_fields = ["user", "total_price", "status", "created_at", "shipping_address"]
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "order", "reference", "amount", "status", "created_at"]


