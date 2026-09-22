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


def register_view(request):
    if request.session.get("access_token"):
        return redirect("kiosco")

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
            # El endpoint de registro de FastAPI todavía no está creado.
            # Cuando esté disponible, aquí conectaremos el formulario
            # con /api/v1/auth/register.
            success = (
                "El formulario está listo. "
                "El registro se habilitará cuando el backend esté disponible."
            )

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