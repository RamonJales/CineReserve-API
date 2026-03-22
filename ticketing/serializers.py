from rest_framework import serializers

from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source="session.movie.title", read_only=True)
    room_name = serializers.CharField(source="session.room.name", read_only=True)
    start_time = serializers.DateTimeField(source="session.start_time", read_only=True)
    row = serializers.CharField(source="seat.row", read_only=True)
    number = serializers.CharField(source="seat.number", read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "movie_title", "room_name", "start_time", "row", "number", "purchased_at")
