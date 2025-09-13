from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
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
        1: ("09:00", "12:00"),
        2: ("12:00", "15:00"),
        3: ("15:00", "18:00"),
    }

    for room in rooms:
        room.sessions = []  # attach sessions to room
        for session_id, (start_str, end_str) in session_times.items():
            start_time = datetime.combine(today, datetime.strptime(start_str, "%H:%M").time())
            end_time = datetime.combine(today, datetime.strptime(end_str, "%H:%M").time())

            is_booked = Booking.objects.filter(
                room=room, start_time=start_time, end_time=end_time
            ).exists()

            room.sessions.append({
                "id": session_id,
                "label": f"{start_str} – {end_str}",
                "is_booked": is_booked,
            })

    # booking handler
    if request.method == "POST":
        room_id = request.POST.get("room_id")
        date_str = request.POST.get("date")
        session = int(request.POST.get("session"))

        room = get_object_or_404(Room, id=room_id)
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        if date == today and now > end_time:
            return redirect("booking:index")

        if date < today or date > max_date:
            return redirect("booking:index")

        start_str, end_str = session_times[session]
        start_time = datetime.combine(date, datetime.strptime(start_str, "%H:%M").time())
        end_time = datetime.combine(date, datetime.strptime(end_str, "%H:%M").time())

        if Booking.objects.filter(room=room, start_time=start_time, end_time=end_time).exists():
            return redirect("booking:index")

        Booking.objects.create(user=request.user, room=room, start_time=start_time, end_time=end_time)
        return redirect("booking:index")

    return render(request, "index.html", {
        "rooms": rooms,
        "today": today,
        "max_date": max_date,
        "selected_date": selected_date,
    })


#def authView(request):
    form = UserCreationForm
    return render(request, "registration/signup.html", {"form" : UserCreationForm})

def login_view(request):
    form = AuthenticationForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by("-start_time")
    return render(request, "my_bookings.html", {"bookings": bookings})


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.delete()
    return redirect("booking:my_bookings")
