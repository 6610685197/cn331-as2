from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Room, Booking


def index(request):
    rooms = Room.objects.all().order_by("number")
    bookings = Booking.objects.all().order_by("start_time")

    if request.method == "POST" and request.user.is_authenticated:
        room_id = request.POST.get("room_id")
        start = request.POST.get("start_time")
        end = request.POST.get("end_time")
        room = get_object_or_404(Room, id=room_id)

        # check conflicts
        conflict = Booking.objects.filter(
            room=room,
            start_time__lt=end,
            end_time__gt=start,
        ).exists()

        if conflict:
            return render(
                request,
                "booking/index.html",
                {
                    "rooms": rooms,
                    "bookings": bookings,
                    "error": f"{room.name} is already booked for that time.",
                },
            )

        Booking.objects.create(
            user=request.user,
            room=room,
            start_time=start,
            end_time=end,
        )
        return redirect("booking:my_bookings")

    return render(
        request,
        "index.html",
        {
            "rooms": rooms,
            "bookings": bookings,
        },
    )


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by("-start_time")
    return render(request, "my_bookings.html", {"bookings": bookings})


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.delete()
    return redirect("booking:my_bookings")
