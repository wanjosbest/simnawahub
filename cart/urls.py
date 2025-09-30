from django.urls import path
from . import views

urlpatterns = [
    path("", views.get_cart, name="get-cart"),                       # GET user cart
    path("add/", views.add_to_cart, name="add-to-cart"),             # POST add item
    path("item/<int:item_id>/update/", views.update_cart_item, name="update-cart-item"), # PUT
    path("item/<int:item_id>/remove/", views.remove_cart_item, name="remove-cart-item"), # DELETE
    path("clear/", views.clear_cart, name="clear-cart"),             # DELETE all cart items
    path("checkout/", views.checkout, name="cart-checkout"),         # POST checkout & initialize payment
]
