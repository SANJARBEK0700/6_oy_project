from django.contrib import admin
from .models import Post, Story, Comment, Like, Follow


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'caption', 'likes_count', 'comments_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['author__username', 'caption']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'created_at', 'expires_at']
    list_filter = ['created_at']
    search_fields = ['author__username']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'parent', 'text', 'created_at']
    list_filter = ['created_at']
    search_fields = ['author__username', 'text']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'comment', 'created_at']
    list_filter = ['created_at']
    search_fields = ['author__username']
    readonly_fields = ['id', 'created_at']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['id', 'follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'following__username']
    readonly_fields = ['id', 'created_at']
