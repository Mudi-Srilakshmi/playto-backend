from datetime import timedelta

from django.db import transaction, IntegrityError
from django.db.models import Count, Sum, Prefetch
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Post, Comment, Like, KarmaTransaction
from .serializers import PostSerializer, LeaderboardSerializer


User = get_user_model()


# -----------------------------
# Utility: Build Comment Tree
# -----------------------------
def build_comment_tree(comments):
    comment_map = {}
    roots = []

    for c in comments:
        comment_map[c.id] = {
            "id": c.id,
            "content": c.content,
            "author": c.author.username,
            "created_at": c.created_at,
            "children": []
        }

    for c in comments:
        if c.parent_id:
            comment_map[c.parent_id]["children"].append(comment_map[c.id])
        else:
            roots.append(comment_map[c.id])

    return roots


# -----------------------------
# Feed API
# -----------------------------
class PostFeedAPIView(APIView):
    def get(self, request):
        posts = (
            Post.objects
            .select_related('author')
            .annotate(like_count=Count('likes'))
            .order_by('-created_at')
        )

        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


# -----------------------------
# Post Detail + Comments
# -----------------------------
class PostDetailAPIView(APIView):
    def get(self, request, post_id):
        post = (
            Post.objects
            .select_related('author')
            .prefetch_related(
                Prefetch(
                    'comments',
                    queryset=Comment.objects.select_related('author')
                )
            )
            .get(id=post_id)
        )

        post_data = PostSerializer(post).data

        comments = post.comments.all()
        post_data["comments"] = build_comment_tree(comments)

        return Response(post_data)


# -----------------------------
# Like API (Concurrency Safe)
# -----------------------------
class LikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        post_id = request.data.get("post_id")
        comment_id = request.data.get("comment_id")

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

        return Response(
            {"message": "Liked successfully"},
            status=status.HTTP_201_CREATED
        )


# -----------------------------
# Leaderboard (Last 24 Hours)
# -----------------------------
class LeaderboardAPIView(APIView):
    def get(self, request):
        last_24_hours = timezone.now() - timedelta(hours=24)

        leaderboard = (
            KarmaTransaction.objects
            .filter(created_at__gte=last_24_hours)
            .values("user__username")
            .annotate(total_karma=Sum("points"))
            .order_by("-total_karma")[:5]
        )

        data = [
            {
                "user": row["user__username"],
                "total_karma": row["total_karma"]
            }
            for row in leaderboard
        ]

        serializer = LeaderboardSerializer(data, many=True)
        return Response(serializer.data)
