from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post

User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "content",
            "created_at",
            "like_count",
        ]


class LeaderboardSerializer(serializers.Serializer):
    user = serializers.CharField()
    total_karma = serializers.IntegerField()
