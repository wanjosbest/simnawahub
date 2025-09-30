from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from listings.models import Product
from .serializers import CartSerializer, CartItemSerializer
from orders.models import Order, OrderItem 
from django.conf import settings
import requests
# ---------------------------
# GET USER CART
# ---------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)

# ---------------------------
# ADD ITEM TO CART
# ---------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity", 1))

    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# ---------------------------
# UPDATE CART ITEM
# ---------------------------
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.data.get("quantity", cart_item.quantity))
    if quantity < 1:
        return Response({"error": "Quantity must be at least 1"}, status=status.HTTP_400_BAD_REQUEST)
    cart_item.quantity = quantity
    cart_item.save()
    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data)

# ---------------------------
# REMOVE CART ITEM
# ---------------------------
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return Response({"success": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT)

# ---------------------------
# CLEAR CART
# ---------------------------
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    return Response({"success": "Cart cleared"}, status=status.HTTP_204_NO_CONTENT)

PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def checkout(request):
    """
    Converts cart items to an Order and initializes Paystack payment.
    """
    user = request.user
    cart = get_object_or_404(Cart, user=user)
    items = cart.items.all()

    if not items.exists():
        return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

    # Create order
    order = Order.objects.create(user=user)
    total_price = 0

    for item in items:
        product = item.product
        quantity = item.quantity
        price = product.price * quantity

        if product.stock < quantity:
            return Response({"error": f"Not enough stock for {product.name}"}, status=status.HTTP_400_BAD_REQUEST)

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )
        total_price += price

        # Reduce stock
        product.stock -= quantity
        product.save()

    order.total_price = total_price
    order.save()

    # Clear cart
    items.delete()

    # Initialize Paystack
    url = "https://api.paystack.co/transaction/initialize"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    data = {
        "email": user.email,
        "amount": int(total_price * 100),  # in kobo
        "metadata": {"order_id": order.id}
    }

    response = requests.post(url, json=data, headers=headers)
    res_data = response.json()

    if res_data.get("status"):
        Payment.objects.update_or_create(
            order=order,
            defaults={
                "reference": res_data["data"]["reference"],
                "amount": total_price,
                "status": "pending"
            }
        )
        return Response({
            "success": "Order created",
            "order_id": order.id,
            "authorization_url": res_data["data"]["authorization_url"]
        }, status=status.HTTP_201_CREATED)

    return Response({"error": "Could not initialize payment"}, status=status.HTTP_400_BAD_REQUEST)