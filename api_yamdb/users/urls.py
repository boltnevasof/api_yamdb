from django.urls import path, include
from api.views import Signup, TokenObtain, UsersViewSet
from rest_framework.routers import DefaultRouter

app_name = 'users'

router = DefaultRouter()
router.register(
    'users',
    UsersViewSet,
    basename='users'
)
urlpatterns = [
    path('auth/signup/', Signup.as_view(), name='signup'),
    path('auth/token/', TokenObtain.as_view(), name='token-obtain'),
    path('', include(router.urls)),

]
