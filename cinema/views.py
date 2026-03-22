from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from .models import Movie, Session
from .serializers import MovieSerializer, SessionSerializer
from .selectors import get_session_seat_map

class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """List all movies available"""
    queryset = Movie.objects.all().order_by("-release_date")
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]

class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    """List sessions (can filter by movie_id)"""
    queryset = Session.objects.all().select_related("movie", "room").order_by("start_time")
    serializer_class = SessionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        movie_id = self.request.query_params.get("movie_id")
        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)
        return queryset

    @action(detail=True, methods=["get"], permission_classes=[AllowAny])
    def seat_map(self, request, pk=None):
        """Seat Map Visualization per movie session"""
        session = self.get_object()

        current_user_id = request.user.id

        seat_map_data = get_session_seat_map(session.id, current_user_id=current_user_id)
        return Response(seat_map_data)