from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from datetime import datetime, timedelta
from .models import Room, Booking


def index(request):
    rooms = Room.objects.all().order_by("number")
    now = timezone.localtime()
    today = timezone.localdate()
    max_date = today + timedelta(days=7)

    # selected date (default: today)
    date_str = request.GET.get("date")
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    # Ensure date is within [today, max_date]
    if selected_date < today:
        selected_date = today
    elif selected_date > max_date:
        selected_date = max_date
    
    session_times = {
        1: ("09:00", "10:00"),
        2: ("10:00", "11:00"),
        3: ("11:00", "12:00"),
        4: ("13:00", "14:00"),
        5: ("14:00", "15:00"),
        6: ("15:00", "16:00"),
    }

    for room in rooms:
        room.sessions = []  # attach sessions to room
        for session_id, (start_str, end_str) in session_times.items():
            start_time = datetime.combine(selected_date, datetime.strptime(start_str, "%H:%M").time())
            end_time = datetime.combine(selected_date, datetime.strptime(end_str, "%H:%M").time())

            is_booked = Booking.objects.filter(
                room=room, start_time=start_time, end_time=end_time
            ).exists()

            room.sessions.append({
                "id": session_id,
                "label": f"{start_str} – {end_str}",
                "is_booked": is_booked,
            })

    # booking
    if request.method == "POST":
        room_id = request.POST.get("room_id")
        date_str = request.POST.get("date")
        session = int(request.POST.get("session"))

        room = get_object_or_404(Room, id=room_id)
        date = datetime.strptime(date_str, "%Y-%m-%d").date()

        if date < today or date > max_date:
            messages.error(request, "Invalid booking date.")
            return redirect(f"{reverse('booking:index')}?date={date}")

        start_str, end_str = session_times[session]
        start_time = datetime.combine(date, datetime.strptime(start_str, "%H:%M").time())
        end_time = datetime.combine(date, datetime.strptime(end_str, "%H:%M").time())

        if Booking.objects.filter(room=room, start_time=start_time, end_time=end_time).exists():
            return redirect(f"{reverse('booking:index')}?date={date}")

        Booking.objects.create(user=request.user, room=room, start_time=start_time, end_time=end_time)
        messages.success(request, f"Your booking for {room.name} on {date} at {start_str} – {end_str} is confirmed!")
        return redirect(f"{reverse('booking:index')}?date={date}")

    return render(request, "index.html", {
        "rooms": rooms,
        "today": today,
        "max_date": max_date,
        "selected_date": selected_date,
    })



@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by("start_time")
    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        date_str = booking.start_time.strftime("%Y-%m-%d")
        time_str = f"{booking.start_time.strftime('%H:%M')} – {booking.end_time.strftime('%H:%M')}"
        
        booking.delete()
        messages.success(request, f"Your booking on {date_str} at {time_str} has been cancelled.")

        return render(request, "my_bookings.html", {"bookings": bookings})
    return render(request, "my_bookings.html", {"bookings": bookings})

