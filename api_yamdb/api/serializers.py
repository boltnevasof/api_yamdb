from django.db import IntegrityError
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import REGEX_USERNAME, ROLE_CHOICES, User


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
            author = request.user
            if Review.objects.filter(title_id=title_id, author=author
                                     ).exists():
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
        slug_field='slug', queryset=Genre.objects.all(), many=True
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
    role = serializers.ChoiceField(choices=ROLE_CHOICES, read_only=True)

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
        max_length=254,
        required=True,
    )
    username = serializers.RegexField(
        regex=REGEX_USERNAME,
        max_length=150,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'username',
        )

    def create(self, validated_data):
        """Создает нового пользователя на основе переданных данных."""
        try:
            user, _ = User.objects.get_or_create(
                username=validated_data.get('username'),
                email=validated_data.get('email'),
            )
        except IntegrityError as error:
            raise serializers.ValidationError(
                'Такое имя пользователя уже существует.'
                if 'username' in str(error)
                else 'Пользователь с таким электронным адресом уже существует.'
            )
        return user

    def validate_username(self, value: str) -> str:
        """Проверка имени пользователя на недопустимые значения."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" недопустимо.'
            )
        return value


class TokenObtainSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
