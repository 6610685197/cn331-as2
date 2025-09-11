from django.db import models
from django.conf import settings

# Create your models here.


class Room(models.Model):
    number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    capacity = models.PositiveBigIntegerField()
    is_open = models.BooleanField(default=True)

    # manage by admin
    def __str__(self):
        return f"{self.number} - {self.name}"


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} booked {self.room.name} ({self.start_time} - {self.end_time})"
