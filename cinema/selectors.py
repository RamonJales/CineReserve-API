import redis
from django.conf import settings
from .models import Session, Seat
from ticketing.models import Ticket

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_session_seat_map(session_id: int, current_user_id: int = None) -> list[dict]:
    session = Session.objects.select_related("room").get(id=session_id)
    all_seats = Seat.objects.filter(room=session.room).order_by("row", "number")
    
    purchased_seat_ids = set(
        Ticket.objects.filter(session=session).values_list("seat_id", flat=True)
    )

    redis_keys = [f"seat_lock:{session.id}:{seat.id}" for seat in all_seats]
    
    redis_values = redis_client.mget(redis_keys)

    seat_map = []
    for seat, redis_val in zip(all_seats, redis_values):
        if seat.id in purchased_seat_ids:
            status = "Purchased"
        elif redis_val:
            if str(current_user_id) == redis_val:
                status = "Reserved (By You)"
            else:
                status = "Reserved"
        else:
            status = "Available"
        
        seat_map.append({
            "seat_id": seat.id,
            "row": seat.row,
            "number": seat.number,
            "status": status
        })
        
    return seat_map