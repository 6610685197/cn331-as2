from django.urls import path
from . import views

app_name = "booking"

urlpatterns = [
    path("", views.index, name="index"),
    path("my-bookings/", views.my_bookings, name="my-bookings"),
    path("cancel/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),
]
