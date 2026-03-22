from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from cinema.models import Movie, Room, Seat, Session

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    return User.objects.create_user(
        email="test@example.com", username="testuser", password="password123"
    )


@pytest.fixture
def auth_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def cinema_setup(db):
    movie = Movie.objects.create(
        title="Dune: Part Two",
        description="Epic sci-fi",
        duration_minutes=166,
        release_date=timezone.now().date(),
    )
    room = Room.objects.create(name="IMAX 1")
    seat = Seat.objects.create(room=room, row="A", number="1")
    session = Session.objects.create(
        movie=movie,
        room=room,
        start_time=timezone.now() + timedelta(days=1),
        end_time=timezone.now() + timedelta(days=1, hours=3),
    )
    return {"movie": movie, "room": room, "session": session, "seat": seat}
