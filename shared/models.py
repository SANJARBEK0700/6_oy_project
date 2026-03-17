
from django.db import models
from users.models import CustomUser
import uuid


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)

    class Meta:
        abstract = True




class Post(BaseModel):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='posts/images/')
    caption = models.TextField(blank=True)

    def __str__(self):
        return f"{self.author.username} - {self.id}"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()

    class Meta:
        ordering = ['-created_at']


class Story(BaseModel):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='stories')
    image = models.ImageField(upload_to='stories/images/', null=True, blank=True)
    video = models.FileField(upload_to='stories/videos/', null=True, blank=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.author.username} - story {self.id}"

    class Meta:
        ordering = ['-created_at']


class Comment(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='replies'
    )
    text = models.TextField()

    def __str__(self):
        return f"{self.author.username}: {self.text[:30]}"

    @property
    def replies_count(self):
        return self.replies.count()

    class Meta:
        ordering = ['created_at']


class Like(BaseModel):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='likes',
        null=True, blank=True
    )
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE,
        related_name='likes',
        null=True, blank=True
    )
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['post', 'author'],
                condition=models.Q(post__isnull=False),
                name='unique_post_like'
            ),
            models.UniqueConstraint(
                fields=['comment', 'author'],
                condition=models.Q(comment__isnull=False),
                name='unique_comment_like'
            ),
        ]

    def __str__(self):
        return f"{self.author.username} liked"


class Follow(BaseModel):
    follower = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='following'
    )
    following = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='followers'
    )

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} -> {self.following.username}"
