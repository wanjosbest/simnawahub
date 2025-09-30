from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from listings.models import Product
from .serializers import OrderSerializer, OrderItemSerializer,ShippingAddressSerializer

# ---------------------------
# CREATE ORDER
# ---------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    """
    Expects payload: { "items": [ { "product_id": 1, "quantity": 2 }, ... ] }
    """
    user = request.user
    data = request.data.get("items", [])

    if not data:
        return Response({"error": "No items provided"}, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.create(user=user)
    total_price = 0

    for item in data:
        product = get_object_or_404(Product, id=item["product_id"])
        quantity = item.get("quantity", 1)
        price = product.price * quantity
        OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)
        total_price += price

    order.total_price = total_price
    order.save()

    serializer = OrderSerializer(order)
    #sendmail
    send_order_notification(
    request.user.email,
    "Order Placed Successfully",
    f"Your order #{order.id} has been placed. Total: ₦{order.total_price}")
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# ---------------------------
# LIST USER ORDERS
# ---------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_orders(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


# ---------------------------
# ORDER DETAIL / UPDATE / CANCEL
# ---------------------------
@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "GET":
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    elif request.method == "PUT":
        # Example: update status
        status_val = request.data.get("status")
        if status_val in dict(Order.STATUS_CHOICES).keys():
            order.status = status_val
            order.save()
            return Response({"success": f"Order status updated to {status_val}"})
        return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        order.delete()
        return Response({"success": "Order deleted"}, status=status.HTTP_204_NO_CONTENT)


import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Order, Payment
from .serializers import PaymentSerializer

PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initialize_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    url = "https://api.paystack.co/transaction/initialize"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    data = {
        "email": request.user.email,
        "amount": int(order.total_price * 100),  # Paystack expects amount in kobo
        "metadata": {"order_id": order.id}
    }

    response = requests.post(url, json=data, headers=headers)
    res_data = response.json()

    if res_data["status"]:
        Payment.objects.update_or_create(
            order=order,
            defaults={"reference": res_data["data"]["reference"], "amount": order.total_price, "status": "pending"}
        )
        return Response({"authorization_url": res_data["data"]["authorization_url"]})
    return Response({"error": "Could not initialize payment"}, status=400)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_payment(request, reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    response = requests.get(url, headers=headers)
    res_data = response.json()

    if res_data["status"] and res_data["data"]["status"] == "success":
        payment = get_object_or_404(Payment, reference=reference)
        payment.status = "success"
        payment.save()

        order = payment.order
        order.status = "completed"
        order.save()
        #send mail
        send_order_notification(
    request.user.email,
    "Payment Successful",
    f"Your order #{order.id} has been paid successfully.")
        return Response({"success": "Payment successful"})
    return Response({"error": "Payment verification failed"}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_shipping_address(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    serializer = ShippingAddressSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user, order=order)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


from django.core.mail import send_mail

def send_order_notification(user_email, subject, message):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )
