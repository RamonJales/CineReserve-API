import redis
from django.conf import settings
from ticketing.models import Ticket
from cinema.models import Session, Seat
from rest_framework.exceptions import ValidationError
from django.db import transaction

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

LOCK_TIMEOUT_SECONDS = 600  # 10 minutes

def reserve_seat(user_id: int, session_id: int, seat_id: int) -> dict:
    """
    Attempts to temporarily lock a seat in Redis for a specific user.
    """
    session = Session.objects.select_related("room").filter(id=session_id).first()
    if not session:
        raise ValidationError("Session not found.")
    
    seat = Seat.objects.filter(id=seat_id, room=session.room).first()
    if not seat:
        raise ValidationError("Seat not found or does not belong to this room.")

    if Ticket.objects.filter(session_id=session_id, seat_id=seat_id).exists():
        raise ValidationError("This seat has already been purchased.")

    lock_key = f"seat_lock:{session_id}:{seat_id}"
    
    acquired = redis_client.set(lock_key, str(user_id), nx=True, ex=LOCK_TIMEOUT_SECONDS)
    
    if not acquired:
        raise ValidationError("This seat is currently reserved by another user.")

    return {
        "message": "Seat successfully reserved for 10 minutes.",
        "session_id": session_id,
        "seat_id": seat_id,
        "expires_in_seconds": LOCK_TIMEOUT_SECONDS
    }


def checkout_ticket(user_id: int, session_id: int, seat_id: int) -> Ticket:
    """
    Converts a temporary Redis reservation into a permanent Ticket record.
    """
    lock_key = f"seat_lock:{session_id}:{seat_id}"
    lock_owner = redis_client.get(lock_key)

    if not lock_owner or str(lock_owner) != str(user_id):
        raise ValidationError("You do not have an active reservation for this seat. It may have expired.")

    try:
        with transaction.atomic():
            ticket = Ticket.objects.create(
                user_id=user_id,
                session_id=session_id,
                seat_id=seat_id
            )
            redis_client.delete(lock_key)
            
            return ticket
            
    except Exception as e:
        raise ValidationError(f"Checkout failed: {str(e)}")