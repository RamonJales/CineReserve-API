from .models import Session, Seat
from ticketing.models import Ticket

def get_session_seat_map(session_id: int) -> list[dict]:
    """
    Returns a list of all seats for a given session with their current status.
    """
    session = Session.objects.select_related("room").get(id=session_id)
    all_seats = Seat.objects.filter(room=session.room).order_by("row", "number")
    
    purchased_seat_ids = set(
        Ticket.objects.filter(session=session).values_list("seat_id", flat=True)
    )

    seat_map = []
    for seat in all_seats:
        status = "Purchased" if seat.id in purchased_seat_ids else "Available"
        
        
        seat_map.append({
            "seat_id": seat.id,
            "row": seat.row,
            "number": seat.number,
            "status": status
        })
        
    return seat_map