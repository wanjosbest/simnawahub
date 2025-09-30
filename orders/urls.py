from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_orders, name="order-list"),
    path("create/", views.create_order, name="order-create"),
    path("<int:order_id>/", views.order_detail, name="order-detail"),
    path("<int:order_id>/pay/", views.initialize_payment, name="initialize-payment"),
    path("verify/<str:reference>/", views.verify_payment, name="verify-payment"),

]
