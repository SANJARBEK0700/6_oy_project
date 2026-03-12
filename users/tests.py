
from django.urls import path
from .views import SignUpView,CodeVerifyView,GetNewCodeView,UserChangeInfoView,UserChangePhotoView

urlpatterns = [
    path('signup/', SignUpView.as_view()),
    path('code-verify/',CodeVerifyView.as_view()),
    path('get-new-code/', GetNewCodeView.as_view()),
    path('change-info/', UserChangeInfoView.as_view()),
    path('change-photo/', UserChangePhotoView.as_view()),
]
