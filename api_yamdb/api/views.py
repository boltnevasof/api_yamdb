from api.filters import TitleFilter
from api.permissions import (AdminOnly, IsAdminOrReadOnly,
                             IsAuthorOrModeratorOrAdmin)
from api.serializers import (AdminUsersSerializer, CategorySerializer,
                             CommentSerializer, GenreSerializer,
                             ReviewSerializer, SignUpSerializer,
                             TitleSerializer, TokenObtainSerializer,
                             UsersSerializer)
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (exceptions, filters, mixins, pagination,
                            permissions, status, viewsets)
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from reviews.models import Category, Genre, Review, Title

User = get_user_model()


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов на произведения."""

    serializer_class = ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin
    )

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        if not partial:
            raise exceptions.MethodNotAllowed('PUT')
        return super().update(request, partial=partial, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев к отзывам."""

    http_method_names = ('get', 'post', 'patch', 'delete')
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrModeratorOrAdmin
    )

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class TitleViewSet(viewsets.ModelViewSet):
    serializer_class = TitleSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
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
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = (IsAuthenticated, AdminOnly)
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
            if request.user.is_admin:
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
        token = serializer.validated_data['token']
        return Response({'token': token}, status=status.HTTP_200_OK)


class Signup(APIView):
    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=(data['to_email'],)
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
