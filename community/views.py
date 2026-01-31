from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Post
from .serializers import PostSerializer


class PostFeedAPIView(APIView):
    def get(self, request):
        posts = (
            Post.objects
            .all()
            .annotate(like_count=Count('likes'))
            .select_related('author')
            .order_by('-created_at')
        )
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

from django.db.models import Prefetch
from .models import Comment
from .serializers import CommentSerializer


class PostDetailAPIView(APIView):
    def get(self, request, post_id):
        post = (
            Post.objects
            .select_related('author')
            .prefetch_related(
                Prefetch(
                    'comments',
                    queryset=Comment.objects
                        .select_related('author')
                        .prefetch_related('replies__author')
                        .filter(parent__isnull=True)
                )
            )
            .get(id=post_id)
        )

        post_data = PostSerializer(post).data
        post_data['comments'] = CommentSerializer(
            post.comments.all(),
            many=True
        ).data

        return Response(post_data)
    
from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Like, KarmaTransaction, Post, Comment


class LikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        post_id = request.data.get('post_id')
        comment_id = request.data.get('comment_id')

        if not post_id and not comment_id:
            return Response(
                {"error": "post_id or comment_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                if post_id:
                    post = Post.objects.get(id=post_id)
                    Like.objects.create(user=user, post=post)

                    KarmaTransaction.objects.create(
                        user=post.author,
                        points=5
                    )

                else:
                    comment = Comment.objects.get(id=comment_id)
                    Like.objects.create(user=user, comment=comment)

                    KarmaTransaction.objects.create(
                        user=comment.author,
                        points=1
                    )

        except IntegrityError:
            return Response(
                {"error": "Already liked"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"message": "Liked successfully"}, status=status.HTTP_201_CREATED)

from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from django.contrib.auth import get_user_model

from .models import KarmaTransaction
from .serializers import LeaderboardSerializer


User = get_user_model()


class LeaderboardAPIView(APIView):
    def get(self, request):
        last_24_hours = timezone.now() - timedelta(hours=24)

        leaderboard = (
            KarmaTransaction.objects
            .filter(created_at__gte=last_24_hours)
            .values('user__username')
            .annotate(total_karma=Sum('points'))
            .order_by('-total_karma')[:5]
        )

        data = [
            {
                "user": row["user__username"],
                "total_karma": row["total_karma"],
            }
            for row in leaderboard
        ]

        serializer = LeaderboardSerializer(data, many=True)
        return Response(serializer.data)

    


