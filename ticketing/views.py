from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Ticket
from .serializers import TicketSerializer
from .services import checkout_ticket, reserve_seat


class ReserveSeatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get("session_id")
        seat_id = request.data.get("seat_id")

        if not session_id or not seat_id:
            return Response(
                {"detail": "session_id and seat_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = reserve_seat(user_id=request.user.id, session_id=session_id, seat_id=seat_id)

        return Response(result, status.HTTP_200_OK)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get("session_id")
        seat_id = request.data.get("seat_id")

        if not session_id or not seat_id:
            return Response(
                {"detail": "session_id and seat_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ticket = checkout_ticket(user_id=request.user.id, session_id=session_id, seat_id=seat_id)

        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyTicketsListView(generics.ListAPIView):
    """'Lists all tickets for the logged-in user"""

    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Ticket.objects.filter(user=self.request.user)
            .select_related("session__movie", "session__room", "seat")
            .order_by("-purchased_at")
        )
