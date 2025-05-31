from rest_framework import generics, status
from .serializers import RegisterSerializer, TokenObtainSerializer
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny


User = get_user_model()

confirmation_codes = {}


class SendConfirmationCodeView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь с таким email не найден."}, status=400)

        code = '{:06d}'.format(random.randint(0, 999999))
        confirmation_codes[email] = {
            'code': code,
            'timestamp': timezone.now()
        }

        # Отправка письма
        send_mail(
            'Код подтверждения',
            f'Ваш код подтверждения: {code}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return Response({"detail": "Код подтверждения отправлен."})


class ObtainTokenView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            code = serializer.validated_data['confirmation_code']

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"detail": "Пользователь не найден."},
                                status=status.HTTP_404_NOT_FOUND)

            stored_code = confirmation_codes.get(user.email)
            if not stored_code or stored_code['code'] != code:
                return Response({"detail": "Неверный код подтверждения."},
                                status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Пользователь успешно зарегистрирован."},
                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
