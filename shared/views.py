from django.shortcuts import render

# Create your views here.
from datetime import datetime

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from shared.utility import check_uuid
from .models import Post, Story, Comment, Like, Follow
from .serializers import (
    PostSerializer, PostCreateSerializer, PostUpdateSerializer,
    StorySerializer,
    CommentSerializer, CommentCreateSerializer, CommentUpdateSerializer,
    LikeSerializer, FollowSerializer,
)





class PostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        following_ids = self.request.user.following.values_list('following_id', flat=True)
        return Post.objects.filter(author_id__in=following_ids)


class PostCreateView(generics.CreateAPIView):
    serializer_class = PostCreateSerializer
    permission_classes = (permissions.IsAuthenticated,)


class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'id'


class PostUpdateView(generics.UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostUpdateSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'id'


class PostDeleteView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'id'

    def get_object(self):
        obj = super().get_object()
        # Serializer ichidagi permission logikasiga mos
        if obj.author != self.request.user:
            raise ValidationError({
                "status": status.HTTP_403_FORBIDDEN,
                "message": "Siz bu postni o'chira olmaysiz"
            })
        return obj


class MyPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)





class StoryListView(generics.ListAPIView):
    serializer_class = StorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        following_ids = self.request.user.following.values_list('following_id', flat=True)
        return Story.objects.filter(
            author_id__in=following_ids,
            expires_at__gte=datetime.now()
        )


class StoryCreateView(generics.CreateAPIView):
    serializer_class = StorySerializer
    permission_classes = (permissions.IsAuthenticated,)


class StoryDeleteView(generics.DestroyAPIView):
    queryset = Story.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'id'

    def get_object(self):
        obj = super().get_object()
        if obj.author != self.request.user:
            raise ValidationError({
                "status": status.HTTP_403_FORBIDDEN,
                "message": "Siz bu storyny o'chira olmaysiz"
            })
        return obj





class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        check_uuid(post_id)
        return Comment.objects.filter(post_id=post_id, parent=None)


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentCreateSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CommentUpdateView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentUpdateSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'id'


class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'id'

    def get_object(self):
        obj = super().get_object()
        if obj.author != self.request.user:
            raise ValidationError({
                "status": status.HTTP_403_FORBIDDEN,
                "message": "Siz bu commentni o'chira olmaysiz"
            })
        return obj






class PostLikeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, post_id):
        check_uuid(post_id)
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise ValidationError({"message": "Post topilmadi"})

        like = Like.objects.filter(post=post, author=request.user)
        if like.exists():
            like.delete()
            return Response({
                "message": "Like olib tashlandi",
                "status": status.HTTP_200_OK,
                "liked": False,
                "likes_count": post.likes_count
            })
        Like.objects.create(post=post, author=request.user)
        return Response({
            "message": "Like qo'shildi",
            "status": status.HTTP_201_CREATED,
            "liked": True,
            "likes_count": post.likes_count
        })


class CommentLikeView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, comment_id):
        check_uuid(comment_id)
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            raise ValidationError({"message": "Comment topilmadi"})

        like = Like.objects.filter(comment=comment, author=request.user)
        if like.exists():
            like.delete()
            return Response({
                "message": "Like olib tashlandi",
                "status": status.HTTP_200_OK,
                "liked": False
            })
        Like.objects.create(comment=comment, author=request.user)
        return Response({
            "message": "Like qo'shildi",
            "status": status.HTTP_201_CREATED,
            "liked": True
        })





class FollowView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, user_id):
        check_uuid(user_id)
        from users.models import CustomUser
        try:
            target = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError({"message": "Foydalanuvchi topilmadi"})

        if target == request.user:
            raise ValidationError({"message": "O'zingizni follow qila olmaysiz"})

        follow = Follow.objects.filter(follower=request.user, following=target)
        if follow.exists():
            follow.delete()
            return Response({
                "message": f"{target.username} unfollow qilindi",
                "status": status.HTTP_200_OK,
                "followed": False
            })
        Follow.objects.create(follower=request.user, following=target)
        return Response({
            "message": f"{target.username} follow qilindi",
            "status": status.HTTP_201_CREATED,
            "followed": True
        })


class FollowerListView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Follow.objects.filter(following=self.request.user)


class FollowingListView(generics.ListAPIView):
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Follow.objects.filter(follower=self.request.user)