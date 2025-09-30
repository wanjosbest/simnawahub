from django.urls import path
from .views import (
    register_view,
    login_view,
    profile_view,
    change_password_view
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", register_view, name="account-register"),
    path("login/", login_view, name="account-login"),           # custom login
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", profile_view, name="account-profile"),
    path("change-password/", change_password_view, name="change-password"),
]
