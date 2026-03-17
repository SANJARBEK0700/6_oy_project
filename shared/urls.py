
from django.urls import path
from .views import (
    PostListView, PostCreateView, PostDetailView,
    PostUpdateView, PostDeleteView, MyPostsView,
    StoryListView, StoryCreateView, StoryDeleteView,
    CommentListView, CommentCreateView,
    CommentUpdateView, CommentDeleteView,
    PostLikeView, CommentLikeView,
    FollowView, FollowerListView, FollowingListView,
)

urlpatterns = [
    path('posts/',                               PostListView.as_view()),
    path('posts/create/',                        PostCreateView.as_view()),
    path('posts/my/',                            MyPostsView.as_view()),
    path('posts/<uuid:id>/',                     PostDetailView.as_view()),
    path('posts/<uuid:id>/update/',              PostUpdateView.as_view()),
    path('posts/<uuid:id>/delete/',              PostDeleteView.as_view()),
    path('stories/',                             StoryListView.as_view()),
    path('stories/create/',                      StoryCreateView.as_view()),
    path('stories/<uuid:id>/delete/',            StoryDeleteView.as_view()),
    path('posts/<uuid:post_id>/comments/',       CommentListView.as_view()),
    path('comments/create/',                     CommentCreateView.as_view()),
    path('comments/<uuid:id>/update/',           CommentUpdateView.as_view()),
    path('comments/<uuid:id>/delete/',           CommentDeleteView.as_view()),
    path('posts/<uuid:post_id>/like/',           PostLikeView.as_view()),
    path('comments/<uuid:comment_id>/like/',     CommentLikeView.as_view()),
    path('users/<uuid:user_id>/follow/',         FollowView.as_view()),
    path('followers/',                           FollowerListView.as_view()),
    path('following/',                           FollowingListView.as_view()),
]
