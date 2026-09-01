from django.urls import path
from .views import *
from .views_admin import *
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
    path('update_student/', UpdateStudentView.as_view(), name='update_student'),
    path('forgot-password/', UserForgotPasswordView.as_view(), name="forgot-password"),
    path('check_email/', CheckEmail.as_view(), name="check_email"),

    path('reset-password/', UserResetPasswordView.as_view(), name="reset-password"),
    path('view-student-detail/<int:id>', GetStudentDetailView.as_view(), name="get-student-detail"),
    path('student-profile-upload/<int:id>', StudentProfileImageUploadView.as_view(), name="student-profile-upload"),

    path('media-access-url/', MediaAccessUrlView.as_view(), name="media-access-url"),


    path('mail-test/', Mail_test.as_view(), name="mail-test"),

    # path('zoom-test/', CreateZoommMeetingAPIView.as_view(), name="zoom-test"),

    

    ## Admin
    path('create_university_student/', CreateUniversityStudentView.as_view(), name="create_university_student"),

    path('create_referal_code/', CreateStudentRefferalCodeView.as_view(), name="create_code"),
    
    path('verify_refferal_code/', VerifyRefferalCodeView.as_view(), name="verify_refferal_code"),

    path('admin_valid_roles/', AdminRoleListView.as_view()),

    path('dashboard/', DashboardAnalytics.as_view()),
    path('lead_dashboard/', DashboardLeadAnalytics.as_view()),
    path('profile_dashboard/', DashboardProfileAnalytics.as_view()),
    path('lead_profile_dashboard/', DashboardLeadProfileAnalytics.as_view()),




    path("server-test/",ServerTestAPIView.as_view(),name="server-test")
    
]