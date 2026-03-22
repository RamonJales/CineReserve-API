import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
def test_user_registration(api_client):
    url = reverse("user-register")
    data = {"email": "new@example.com", "username": "newuser", "password": "securepassword"}
    response = api_client.post(url, data)
    assert response.status_code == 201
    assert User.objects.filter(email="new@example.com").exists()


@pytest.mark.django_db
def test_user_login(api_client, test_user):
    url = reverse("token_obtain_pair")
    data = {"email": "test@example.com", "password": "password123"}
    response = api_client.post(url, data)
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data
