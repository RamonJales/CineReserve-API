import uuid
from django.db import models
from django.conf import settings
from cinema.models import Session, Seat

class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    session = models.ForeignKey(Session, on_delete=models.PROTECT, related_name="tickets")
    seat = models.ForeignKey(Seat, on_delete=models.PROTECT, related_name="tickets")
    
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("session", "seat")

    def __str__(self):
        return f"Ticket {self.id} - {self.user.email}"