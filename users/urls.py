from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    path("login/", UserLoginView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    path('create_student/', CreateStudentView.as_view(), name='create_student'),
    path('forgot-password/', UserForgotPasswordView.as_view(), name="forgot-password"),

    path('reset-password/', UserResetPasswordView.as_view(), name="reset-password"),
    path('view-student-detail-test/<int:id>', GetStudentDetailView_Test.as_view(), name="get-student-detail-test"),
]