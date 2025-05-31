from rest_framework import viewsets, permissions, status, views
from rest_framework.generics import get_object_or_404

from reviews.models import Review, Title
from api.serializers import (
    ReviewSerializer,
    CommentSerializer,
)
from api.permissions import IsAuthorOrModeratorOrAdmin
from rest_framework.response import Response


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов на произведения."""
    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin
    )

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев к отзывам."""
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin
    )

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, review=review)
