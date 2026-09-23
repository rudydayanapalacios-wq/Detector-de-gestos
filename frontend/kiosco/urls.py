from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("login/", views.login_view, name="login_page"),
    path("register/", views.register_view, name="register"),
    path("kiosco/", views.kiosco, name="kiosco"),
    path("gestos/", views.gestos, name="gestos"),
    path("imagenes/", views.imagenes, name="imagenes"),
    path("logout/", views.logout_view, name="logout"),
]