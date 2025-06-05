from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import (
    filters,
    mixins,
    pagination,
    permissions,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,
)

from api.filters import TitleFilter
from api.permissions import IsAuthorOrModeratorOrAdmin, IsAdminOrReadOnly, AdminOnly
from api.serializers import (
    SignUpSerializer,
    UsersSerializer,
    TokenObtainSerializer,
    AdminUsersSerializer,
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleSerializer,
)

User = get_user_model()


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


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name', 'genre__slug', 'category__slug')
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        queryset = Title.objects.all()
        return (
            queryset
            .order_by('-year')
            .annotate(rating=Avg('reviews__score'))
        )


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    permission_classes = (IsAdminOrReadOnly,)


class UsersViewSet(ModelViewSet):
    """ Представление для работы с пользователями в системе."""
    serializer_class = AdminUsersSerializer
    queryset = User.objects.order_by('username').all()
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAuthenticated, AdminOnly]
    filter_backends = (SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=('GET', 'PATCH'),
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me'
    )
    def get_user_detail(self, request):
        serializer = UsersSerializer(request.user)

        if request.method == 'PATCH':
            if request.user.role == 'admin':
                serializer = AdminUsersSerializer(
                    request.user,
                    data=request.data,
                    partial=True
                )
            else:
                serializer = UsersSerializer(
                    request.user,
                    data=request.data,
                    partial=True
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)


class TokenObtain(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            raise NotFound(detail={'username': 'Пользователь не найден'})
        if data.get('confirmation_code') == user.confirmation_code:
            token = RefreshToken.for_user(user).access_token
            raise ValidationError({'token': str(token)})
        return Response(
            {'confirmation_code': 'Неверный код подтверждения!'},
            status=status.HTTP_400_BAD_REQUEST)


class Signup(APIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=[data['to_email']]
        )
        email.send()

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        email_body = (
            f'Код подтвержения для доступа к API: {user.confirmation_code}'
        )
        data = {
            'email_body': email_body,
            'to_email': user.email,
            'email_subject': 'Код подтвержения для доступа к API!'
        }
        self.send_email(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

