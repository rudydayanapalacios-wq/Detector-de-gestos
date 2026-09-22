import requests

from django.conf import settings
from django.shortcuts import redirect, render


def login_view(request):
    if request.session.get("access_token"):
        return redirect("kiosco")

    error = None

    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        try:
            response = requests.post(
                f"{settings.FASTAPI_URL}/api/v1/auth/login",
                data={
                    "username": username,
                    "password": password,
                },
                timeout=5,
            )

            response.raise_for_status()

            token_data = response.json()

            request.session["access_token"] = token_data["access_token"]
            request.session["username"] = username

            return redirect("kiosco")

        except requests.RequestException:
            error = "No fue posible conectar con el backend."

        except KeyError:
            error = "El backend respondió con un formato inesperado."

    return render(
        request,
        "kiosco/login.html",
        {"error": error},
    )


def kiosco(request):
    if not request.session.get("access_token"):
        return redirect("login")

    return render(
        request,
        "kiosco/kiosco.html",
        {
            "username": request.session.get("username"),
            "access_token": request.session.get("access_token"),
            "fastapi_url": settings.FASTAPI_URL,
        },
    )


def logout_view(request):
    if request.method == "POST":
        request.session.flush()

    return redirect("login")