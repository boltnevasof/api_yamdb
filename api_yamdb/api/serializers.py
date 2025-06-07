from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import REGEX_USERNAME, RoleChoices

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    pub_date = serializers.DateTimeField(read_only=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        """Проверка: один отзыв на одно произведение от одного пользователя."""
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')

        if request.method == 'POST':
            title = get_object_or_404(Title, id=title_id)
            author = request.user
            if title.reviews.filter(author=author).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение.'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    pub_date = serializers.DateTimeField(read_only=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    # Сериализатор для жанра
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    rating = serializers.IntegerField(read_only=True)
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        allow_empty=True
    )

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['genre'] = GenreSerializer(
            instance.genre.all(), many=True
        ).data
        representation['category'] = CategorySerializer(instance.category).data
        return representation


class UsersSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=RoleChoices.choices, read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')


class AdminUsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role')


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        max_length=User._meta.get_field('email').max_length,
    )
    username = serializers.CharField(
        required=True,
        max_length=User._meta.get_field('username').max_length,
        validators=[
            RegexValidator(
                regex=REGEX_USERNAME,
                message='Введите правильное имя пользователя.',
                code='invalid_username'
            )
        ]
    )

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" недопустимо.'
            )
        return value

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        user_with_username = User.objects.filter(username=username).first()
        user_with_email = User.objects.filter(email=email).first()

        if user_with_username and user_with_username.email != email:
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует.'
            )

        if user_with_email and user_with_email.username != username:
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )

        return data

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(**validated_data)
        return user


class TokenObtainSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        user = get_object_or_404(User, username=username)

        if confirmation_code != user.confirmation_code:
            raise ValidationError(
                {'confirmation_code': 'Неверный код подтверждения!'})

        token = RefreshToken.for_user(user).access_token
        data['token'] = str(token)
        return data
