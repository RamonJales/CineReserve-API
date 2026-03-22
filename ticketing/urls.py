from django.urls import path

from .views import CheckoutView, MyTicketsListView, ReserveSeatView

urlpatterns = [
    path("reserve/", ReserveSeatView.as_view(), name="reserve-seat"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("my-tickets/", MyTicketsListView.as_view(), name="my-tickets"),
]
