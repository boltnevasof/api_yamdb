from django.urls import path, include
from rest_framework import routers
from api.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    Signup,
    TitleViewSet,
    TokenObtain,
    UsersViewSet
)

review_list = ReviewViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
review_detail = ReviewViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy'
})

comment_list = CommentViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
comment_detail = CommentViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy'
})

router = routers.DefaultRouter()
router.register('users', UsersViewSet, basename='users')
router.register(r'titles', TitleViewSet, basename='titles')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'genres', GenreViewSet, basename='genres')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', Signup.as_view(), name='signup'),
    path('auth/token/', TokenObtain.as_view(), name='token-obtain'),
    path(
        'titles/<int:title_id>/reviews/',
        review_list,
        name='review-list'
    ),
    path(
        'titles/<int:title_id>/reviews/<int:pk>/',
        review_detail,
        name='review-detail'
    ),
    path(
        'titles/<int:title_id>/reviews/<int:review_id>/comments/',
        comment_list,
        name='comment-list'
    ),
    path(
        'titles/<int:title_id>/reviews/<int:review_id>/comments/<int:pk>/',
        comment_detail,
        name='comment-detail'
    )
]
