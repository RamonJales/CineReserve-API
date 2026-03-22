from unittest.mock import patch

import pytest
from django.urls import reverse

from ticketing.models import Ticket


@pytest.mark.django_db
@patch("ticketing.services.redis_client")
def test_reserve_seat_success(mock_redis, auth_client, cinema_setup):
    mock_redis.set.return_value = True  # Simulate acquiring the lock

    url = reverse("reserve-seat")
    data = {"session_id": cinema_setup["session"].id, "seat_id": cinema_setup["seat"].id}
    response = auth_client.post(url, data)
    assert response.status_code == 200
    assert "successfully reserved" in response.data["message"]


@pytest.mark.django_db
@patch("ticketing.services.redis_client")
def test_checkout_success(mock_redis, auth_client, test_user, cinema_setup):
    # Simulate that Redis says this user owns the lock
    mock_redis.get.return_value = str(test_user.id)
    mock_redis.delete.return_value = 1

    url = reverse("checkout")
    data = {"session_id": cinema_setup["session"].id, "seat_id": cinema_setup["seat"].id}
    response = auth_client.post(url, data)

    assert response.status_code == 201
    assert Ticket.objects.count() == 1
    assert response.data["movie_title"] == "Dune: Part Two"


@pytest.mark.django_db
def test_my_tickets_portal(auth_client, test_user, cinema_setup):
    Ticket.objects.create(
        user=test_user, session=cinema_setup["session"], seat=cinema_setup["seat"]
    )

    url = reverse("my-tickets")
    response = auth_client.get(url)
    assert response.status_code == 200
    assert len(response.data["results"]) == 1
