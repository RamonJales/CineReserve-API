from unittest.mock import patch

import pytest
from django.core import mail
from django.urls import reverse
from rest_framework.exceptions import ValidationError

from ticketing.models import Ticket
from ticketing.tasks import send_ticket_confirmation


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


@pytest.mark.django_db
def test_send_ticket_confirmation_task_success():
    """
    Testa se a função interna da task do Celery funciona,
    gera a string correta e coloca o email na caixa de saída.
    """
    # Executa a task diretamente (síncrona para o teste)
    result = send_ticket_confirmation(
        ticket_id="uuid-1234",
        user_email="test@example.com",
        movie_title="Dune: Part Two",
        session_time="23/03/2026 19:00",
    )

    # 1. Verifica o retorno da task
    assert "Email enviado com sucesso" in result

    # 2. Verifica se o email foi para a 'outbox' (caixa de saída simulada do Django)
    assert len(mail.outbox) == 1

    # 3. Verifica os dados do email enviado
    sent_email = mail.outbox[0]
    assert sent_email.to == ["test@example.com"]
    assert "Dune: Part Two" in sent_email.subject
    assert "uuid-1234" in sent_email.body


@pytest.mark.django_db
@patch("ticketing.services.redis_client")
@patch("ticketing.services.transaction.on_commit")
@patch("ticketing.services.send_ticket_confirmation.delay")
def test_checkout_success_triggers_celery_task(
    mock_task_delay, mock_on_commit, mock_redis, test_user, cinema_setup
):
    """
    Testa se um checkout BEM SUCEDIDO agenda a task no Celery via on_commit.
    """
    # Faz o mock do on_commit executar a função lambda imediatamente
    mock_on_commit.side_effect = lambda f: f()

    # Simula que o lock do Redis pertence ao usuário
    mock_redis.get.return_value = str(test_user.id)
    mock_redis.delete.return_value = 1

    # Faz o checkout real
    from ticketing.services import checkout_ticket

    ticket = checkout_ticket(
        user_id=test_user.id, session_id=cinema_setup["session"].id, seat_id=cinema_setup["seat"].id
    )

    # Verifica se a task do Celery foi chamada com os argumentos exatos do ingresso gerado!
    mock_task_delay.assert_called_once_with(
        str(ticket.id),
        test_user.email,
        cinema_setup["session"].movie.title,
        ticket.session.start_time.strftime("%d/%m/%Y %H:%M"),
    )


@pytest.mark.django_db
@patch("ticketing.services.redis_client")
@patch("ticketing.services.send_ticket_confirmation.delay")
def test_checkout_failure_does_not_trigger_task(
    mock_task_delay, mock_redis, test_user, cinema_setup
):
    """
    Garante que se o checkout FALHAR (ex: lock expirou ou é de outro usuário),
    nenhum ingresso falso será enviado por email.
    """
    # Simula que o lock do Redis pertence a OUTRO usuário (ID 999)
    mock_redis.get.return_value = "999"

    from ticketing.services import checkout_ticket

    # O checkout deve lançar um erro de validação
    with pytest.raises(ValidationError) as exc:
        checkout_ticket(
            user_id=test_user.id,
            session_id=cinema_setup["session"].id,
            seat_id=cinema_setup["seat"].id,
        )

    assert "You do not have an active reservation" in str(exc.value)

    # A prova de fogo: A task do Celery NUNCA deve ter sido chamada
    mock_task_delay.assert_not_called()
