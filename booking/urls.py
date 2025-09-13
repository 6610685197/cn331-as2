from django.urls import path, include
from . import views

app_name = "booking"

urlpatterns = [
    path("", views.index, name="index"),
    path("my-bookings/", views.my_bookings, name="my-bookings"),
    path("signup/", views.authView, name="authView"),
    path("login/", views.login_view, name="login"),
    path("", include("django.contrib.auth.urls")),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

]
