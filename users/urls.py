from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    path("login/", UserLoginView.as_view()),
    path("website_login/", WebsiteUserLoginView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('view-admin-detail/<int:id>', GetAdminDetailView.as_view(), name="get-admin-detail"),


    path('create_student/', CreateStudentView.as_view(), name='create_student'),
    path('forgot-password/', UserForgotPasswordView.as_view(), name="forgot-password"),

    path('reset-password/', UserResetPasswordView.as_view(), name="reset-password"),
    path('view-student-detail/<int:id>', GetStudentDetailView.as_view(), name="get-student-detail"),
    path('student-profile-upload/<int:id>', StudentProfileImageUploadView.as_view(), name="student-profile-upload"),

    path('media-access-url/', MediaAccessUrlView.as_view(), name="media-access-url"),




    path('mail-test/', Mail_test.as_view(), name="mail-test"),
]