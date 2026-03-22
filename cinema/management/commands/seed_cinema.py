from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from cinema.models import Movie, Room, Seat, Session


class Command(BaseCommand):
    help = "Seeds the database with a movie, a room, seats, and a session for testing."

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        # 1. Create a Movie
        movie, _ = Movie.objects.get_or_create(
            title="Dune: Part Two",
            defaults={
                "description": "Paul Atreides unites with Chani and the Fremen...",
                "duration_minutes": 166,
                "release_date": "2024-03-01",
            },
        )

        # 2. Create a Room
        room, created_room = Room.objects.get_or_create(name="IMAX - Room 1")

        # 3. Create Seats (Only if room was just created)
        if created_room:
            seats = []
            rows = ["A", "B", "C", "D", "E"]
            for row in rows:
                for num in range(1, 11):  # 10 seats per row
                    seats.append(Seat(room=room, row=row, number=str(num)))
            Seat.objects.bulk_create(seats)
            self.stdout.write(f"Created 50 seats for {room.name}.")

        # 4. Create a Session
        session, _ = Session.objects.get_or_create(
            movie=movie,
            room=room,
            defaults={
                "start_time": timezone.now() + timedelta(days=1),
                "end_time": timezone.now() + timedelta(days=1, minutes=166),
            },
        )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully seeded! Session ID: {session.id} ready for testing.")
        )
