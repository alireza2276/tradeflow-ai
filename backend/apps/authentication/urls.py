from django.urls import path

from apps.authentication import views


urlpatterns = [
    path(
        "csrf/",
        views.csrf_token_view,
        name="csrf-token",
    ),
    path(
        "login/",
        views.login_view,
        name="login",
    ),

    path(
        "me/",
        views.me_view,
        name="me",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),
]