import time

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_ticket_confirmation(ticket_id: str, user_email: str, movie_title: str, session_time: str):
    """
    Task executed in the background by Celery.
    Simulates the generation of a large PDF and the sending of an email.
    """

    # just for simulating the pdf generations
    time.sleep(2)

    subject = f" Seu ingresso para {movie_title} está confirmado!"
    message = (
        f"Olá!\n\n"
        f"Seu ingresso (ID: {ticket_id}) para a sessão de '{movie_title}' "
        f"em {session_time} foi gerado com sucesso.\n\n"
        f"[Anexo Simulado: ingresso_{ticket_id}.pdf]\n\n"
        f"Bom filme,\nEquipe Cinépolis Natal"
    )

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )

    return f"Email enviado com sucesso para {user_email}"
