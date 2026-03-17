
from rest_framework import serializers
from datetime import datetime, timedelta
from rest_framework.exceptions import ValidationError
from rest_framework import status

from shared.utility import validate_image_size, validate_video_size
from .models import Post, Story, Comment, Like, Follow
from users.models import CustomUser




class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = serializers.StringRelatedField(read_only=True)
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'image', 'caption',
            'likes_count', 'comments_count', 'is_liked',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(author=request.user).exists()
        return False

    def validate_image(self, image):
        validate_image_size(image)
        return image

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise ValidationError({
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Avtorizatsiyadan o'ting"
            })
        return attrs


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['image', 'caption']

    def validate_image(self, image):
        validate_image_size(image)
        return image

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise ValidationError({
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Avtorizatsiyadan o'ting"
            })
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        return Post.objects.create(author=request.user, **validated_data)


class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['caption']

    def validate(self, attrs):
        request = self.context.get('request')
        post = self.instance
        if post.author != request.user:
            raise ValidationError({
                "status": status.HTTP_403_FORBIDDEN,
                "message": "Siz bu postni tahrirlay olmaysiz"
            })
        return attrs






class StorySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Story
        fields = [
            'id', 'author', 'image', 'video',
            'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'expires_at']

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise ValidationError({
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Avtorizatsiyadan o'ting"
            })
        if not attrs.get('image') and not attrs.get('video'):
            raise ValidationError({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Rasm yoki video kiritish majburiy"
            })
        return attrs

    def validate_image(self, image):
        if image:
            validate_image_size(image)
        return image

    def validate_video(self, video):
        if video:
            validate_video_size(video)
        return video

    def create(self, validated_data):
        request = self.context['request']
        expires_at = datetime.now() + timedelta(hours=24)
        return Story.objects.create(
            author=request.user,
            expires_at=expires_at,
            **validated_data
        )






class CommentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = serializers.StringRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()
    replies_count = serializers.ReadOnlyField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'post', 'parent', 'text',
            'replies', 'replies_count',
            'likes_count', 'is_liked',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(
                obj.replies.all(), many=True,
                context=self.context
            ).data
        return []

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(author=request.user).exists()
        return False


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['post', 'parent', 'text']

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise ValidationError({
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Avtorizatsiyadan o'ting"
            })
        parent = attrs.get('parent')
        post = attrs.get('post')
        if parent and parent.post != post:
            raise ValidationError({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Parent comment boshqa postga tegishli"
            })
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        return Comment.objects.create(author=request.user, **validated_data)


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text']

    def validate(self, attrs):
        request = self.context.get('request')
        comment = self.instance
        if comment.author != request.user:
            raise ValidationError({
                "status": status.HTTP_403_FORBIDDEN,
                "message": "Siz bu commentni tahrirlay olmaysiz"
            })
        return attrs





class LikeSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'author', 'post', 'comment', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise ValidationError({
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Avtorizatsiyadan o'ting"
            })
        if not attrs.get('post') and not attrs.get('comment'):
            raise ValidationError({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Post yoki comment ko'rsatilishi shart"
            })
        return attrs






class FollowSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    follower = serializers.StringRelatedField(read_only=True)
    following = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['id', 'follower', 'following', 'created_at']

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise ValidationError({
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Avtorizatsiyadan o'ting"
            })
        return attrs
