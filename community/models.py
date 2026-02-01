from django.db import models
from django.conf import settings


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post {self.id} by {self.author}"


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment {self.id} on Post {self.post_id}"


class PostLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_likes"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="unique_user_post_like"
            )
        ]

    def __str__(self):
        return f"{self.user} liked Post {self.post_id}"


class CommentLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comment_likes"
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "comment"],
                name="unique_user_comment_like"
            )
        ]

    def __str__(self):
        return f"{self.user} liked Comment {self.comment_id}"


class KarmaTransaction(models.Model):
    POST_LIKE = "POST_LIKE"
    COMMENT_LIKE = "COMMENT_LIKE"

    SOURCE_CHOICES = [
        (POST_LIKE, "Post Like"),
        (COMMENT_LIKE, "Comment Like"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="karma_transactions"
    )
    points = models.IntegerField()
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.points} karma to {self.user} ({self.source})"
