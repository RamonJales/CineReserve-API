from django.db import models
from django.core.validators import MinValueValidator

class Movie(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    release_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Room(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Seat(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="seats")
    row = models.CharField(max_length=5)
    number = models.CharField(max_length=5)

    class Meta:
        unique_together = ("room", "row", "number")

    def __str__(self):
        return f"{self.room.name} - {self.row}{self.number}"

class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="sessions")
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="sessions")
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.movie.title} at {self.start_time.strftime('%Y-%m-%d %H:%M')}"