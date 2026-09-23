import requests

from django.conf import settings
from django.shortcuts import redirect, render


def login_view(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
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
        {
            "error": error,
        },
    )


def register_view(request):
    error = None
    success = None

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")

        if not username or not password or not password_confirm:
            error = "Completa todos los campos."

        elif password != password_confirm:
            error = "Las contraseñas no coinciden."

        elif len(password) < 6:
            error = "La contraseña debe tener al menos 6 caracteres."

        else:
            try:
                response = requests.post(
                    f"{settings.FASTAPI_URL}/api/v1/auth/register",
                    json={
                        "username": username,
                        "password": password,
                    },
                    timeout=5,
                )

                if response.status_code == 400:
                    try:
                        error = response.json().get(
                            "detail",
                            "No fue posible crear la cuenta.",
                        )
                    except ValueError:
                        error = "No fue posible crear la cuenta."

                else:
                    response.raise_for_status()

                    data = response.json()

                    success = data.get(
                        "message",
                        "Usuario registrado correctamente.",
                    )

            except requests.RequestException:
                error = "No fue posible conectar con el backend."

            except (KeyError, ValueError):
                error = "El backend respondió con un formato inesperado."

    return render(
        request,
        "kiosco/registro.html",
        {
            "error": error,
            "success": success,
        },
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

def gestos(request):
    if not request.session.get("access_token"):
        return redirect("login")

    return render(
        request,
        "kiosco/gestos.html",
        {
            "username": request.session.get("username"),
            "access_token": request.session.get("access_token"),
            "fastapi_url": settings.FASTAPI_URL,
        },
    )

def imagenes(request):
    if not request.session.get("access_token"):
        return redirect("login")

    return render(
        request,
        "kiosco/imagenes.html",
        {
            "username": request.session.get("username"),
            "access_token": request.session.get("access_token"),
            "fastapi_url": settings.FASTAPI_URL,
        },
    )