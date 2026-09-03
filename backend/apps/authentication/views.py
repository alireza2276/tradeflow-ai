import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

def serialize_user(user):
    roles = list(
        user.groups.order_by("name").values_list(
            "name",
            flat=True,
        )
    )

    permissions = sorted(
        user.get_all_permissions()
    )

    return {
        "id": user.pk,
        "username": user.get_username(),
        "is_staff": user.is_staff,
        "roles": roles,
        "permissions": permissions,
    }

@ensure_csrf_cookie
def csrf_token_view(request):
    if request.method != "GET":
        return JsonResponse(
            {"detail": "Method not allowed."},
            status=405,
        )

    return JsonResponse(
        {"detail": "CSRF cookie set."},
        status=200,
    )


@require_POST
def login_view(request):
    try:
        payload = json.loads(
            request.body.decode("utf-8")
        )
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"detail": "Invalid JSON payload."},
            status=400,
        )

    username = payload.get("username")
    password = payload.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return JsonResponse(
            {"detail": "Username and password are required."},
            status=400,
        )

    username = username.strip()

    if not username or not password:
        return JsonResponse(
            {"detail": "Username and password are required."},
            status=400,
        )

    user = authenticate(
        request=request,
        username=username,
        password=password,
    )

    if user is None:
        return JsonResponse(
            {"detail": "Invalid credentials."},
            status=401,
        )

    login(
        request,
        user,
    )

    return JsonResponse(
        {
            "detail": "Login successful.",
            "user": serialize_user(user),
        },
        status=200,
    )

def me_view(request):
    if request.method != "GET":
        return JsonResponse(
            {"detail": "Method not allowed."},
            status=405,
        )

    if not request.user.is_authenticated:
        return JsonResponse(
            {"detail": "Authentication required."},
            status=401,
        )

    return JsonResponse(
        {
            "user": serialize_user(request.user),
        },
        status=200,
    )

@require_POST
def logout_view(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"detail": "Authentication required."},
            status=401,
        )

    logout(request)

    return JsonResponse(
        {"detail": "Logout successful."},
        status=200,
    )