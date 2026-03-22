from unittest.mock import patch

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_list_movies(api_client, cinema_setup):
    url = reverse("movie-list")
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["title"] == "Dune: Part Two"


@pytest.mark.django_db
@patch("cinema.selectors.redis_client")  # <- AQUI ESTÁ A MÁGICA!
def test_seat_map_unauthenticated(mock_redis, api_client, cinema_setup):
    # Simulamos que o Redis retornou "vazio" (nenhum assento bloqueado)
    mock_redis.mget.return_value = [None]

    session = cinema_setup["session"]
    url = reverse("session-seat-map", args=[session.id])
    response = api_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["status"] == "Available"
