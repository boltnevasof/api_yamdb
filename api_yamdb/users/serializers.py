from rest_framework import serializers

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                "Использовать имя 'me' запрещено.")
        return value

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(required=True)
