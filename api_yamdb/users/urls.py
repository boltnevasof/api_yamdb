from django.urls import path
from .views import ObtainTokenView
from .views import RegisterView, SendConfirmationCodeView


urlpatterns = [
    path('signup/', RegisterView.as_view(), name='register'),
    path('send-confirmation/', SendConfirmationCodeView.as_view(),
         name='send-confirmation'),
    path('token/', ObtainTokenView.as_view(), name='token-obtain'),
]
