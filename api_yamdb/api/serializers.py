from rest_framework import serializers
from reviews.models import Review, Comment


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
            if Review.objects.filter(title_id=title_id, author=author).exists():
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
