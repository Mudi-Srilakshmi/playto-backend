from django.contrib import admin
from django.urls import path

from community.views import (
    PostFeedAPIView,
    PostDetailAPIView,
    LikeAPIView,
    LeaderboardAPIView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/posts/', PostFeedAPIView.as_view()),
    path('api/posts/<int:post_id>/', PostDetailAPIView.as_view()),
    path('api/like/', LikeAPIView.as_view()),
    path('api/leaderboard/', LeaderboardAPIView.as_view()),
]
