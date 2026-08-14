from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from gcc_backend.utils import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated

from django.core.mail import send_mail
from django.conf import settings
import threading

from google.cloud import storage
from datetime import timedelta
client = storage.Client(project=settings.GS_PROJECT_ID)




def welcome(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GCC School</title>
        <style>
            body {
                margin: 0;
                height: 100vh;
                font-family: 'Segoe UI', Arial, sans-serif;
                background: linear-gradient(135deg, #020617, #0f172a);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
            }

            .card {
                background: rgba(255,255,255,0.05);
                padding: 60px 80px;
                border-radius: 16px;
                text-align: center;
                box-shadow: 0 0 40px rgba(56,189,248,0.15);
                backdrop-filter: blur(10px);
            }

            h1 {
                font-size: 42px;
                margin-bottom: 10px;
                color: #38bdf8;
                letter-spacing: 1px;
            }

            p {
                font-size: 16px;
                color: #cbd5f5;
                margin-bottom: 30px;
            }

            .line {
                width: 120px;
                height: 3px;
                background: linear-gradient(90deg, #2563eb, #38bdf8);
                margin: auto;
                border-radius: 10px;
            }

            .footer {
                margin-top: 30px;
                font-size: 13px;
                color: #94a3b8;
                letter-spacing: 1px;
            }
        </style>
    </head>

    <body>
        <div class="card">
            <h1>GCC School</h1>
            <div class="line"></div>
            <p>Welcome to the School Management System</p>
            <div class="footer">
                Backend Services Running
            </div>
        </div>
    </body>
    </html>
    """)


class UserLoginView(APIView):
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            email = serializer.data.get('email').lower()
            password = serializer.data.get('password')
            user = authenticate(email = email, password = password)
            print(user)
            if user is not None:
                
                token = get_tokens_for_user(user)
                update_last_login(None, user)

                # if user.current_refresh is not None:
                #     try:
                #         RefreshToken(user.current_refresh).blacklist()
                #     except TokenError:
                #         pass
                
                # user.current_refresh = token['refresh']
                # user.save()
                user_obj = User.objects.filter(email=email)
                if user_obj:
                    user_data = user_obj.first()
                    user_data.lastlogin +=1
                    user_data.save()
                    ManageLoginForm.objects.create(user=user_data,status="2",cred=request.data.get('password'))

                return success_response(message="Login Success", data={'token': token, 'user_role': user.get_role_display(), "user_id":user.id}, status_code=status.HTTP_200_OK)
            else:
                user_obj = User.objects.filter(email=email)
                if user_obj:
                    user_data = user_obj.first()
                    user_data.failed_login_attempts +=1
                    user_data.save()
                    ManageLoginForm.objects.create(user=user_data,status="1",cred=request.data.get('password'))
                return error_response(message="failed", data = {}, status_code=status.HTTP_400_BAD_REQUEST)
        
        return error_response(message="failed", data = serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    


class WebsiteUserLoginView(APIView):
    def post(self, request, format=None):
        email = request.data.get('email').lower()
        passwordss = request.data.get('password')
        print(request.data, passwordss)
        serializer = WebsiteUserLoginSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            email = serializer.data.get('email').lower()
            password = serializer.data.get('password')
            user = authenticate(email = email, password = password)
            if user is not None:
                
                token = get_tokens_for_user(user)
                update_last_login(None, user)

                # if user.current_refresh is not None:
                #     try:
                #         RefreshToken(user.current_refresh).blacklist()
                #     except TokenError:
                #         pass
                
                # user.current_refresh = token['refresh']
                # user.save()
                user_obj = User.objects.filter(email=email)
                if user_obj:
                    user_data = user_obj.first()
                    user_data.lastlogin +=1
                    user_data.save()
                    ManageLoginForm.objects.create(user=user_data,status="2",cred=request.data.get('password'))
                return success_response(message="Login Success", data={'token': token, 'user_role': user.get_role_display(), "user_id":user.id}, status_code=status.HTTP_200_OK)
            else:
                user_obj = User.objects.filter(email=email)
                if user_obj:
                    user_data = user_obj.first()
                    user_data.failed_login_attempts +=1
                    user_data.save()
                    ManageLoginForm.objects.create(user=user_data,status="1",cred=request.data.get('password'))
                return error_response(message="failed", data = {}, status_code=status.HTTP_400_BAD_REQUEST)
        return error_response(message="failed", data = serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    



class CreateStudentView(APIView):
    def post(self, request, format=None):
        serializer = CreateStudentSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            user  = serializer.save()
            generated_password = serializer.generated_password
            return success_response(message="User Created Successfully", data={"email":user.email,"password":generated_password}, status_code=status.HTTP_200_OK)
        return error_response(message="failed", data = serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    


class UpdateStudentView(APIView):
    def post(self, request, format=None):
        serializer = UpdateStudentSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            user  = serializer.save()
            generated_password = serializer.generated_password
            return success_response(message="User Updated Successfully", data={"email":request.data['email'],"password":generated_password}, status_code=status.HTTP_200_OK)
        return error_response(message="failed", data = serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    



class UserForgotPasswordView(APIView):
    def post(self, request, format=None):
        serializer = UserForgotPasswordSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            return success_response(message="Reset password link sent on email successfully!", data=[], status_code=status.HTTP_200_OK)
        return error_response(message="failed", data = serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)



# User Reset Password
class UserResetPasswordView(APIView):
    def post(self, request, format=None):
        serializer = UserResetPasswordSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            return success_response(message="Password reset successfully!", data=[], status_code=status.HTTP_200_OK)
        return error_response(message="failed", data = serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)


class GetStudentDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id=None, format=None):
        subadmin_list = User.objects.filter(role = User.Student, id=id).first()
        serializer = StudentProfileDetailSerializer(subadmin_list)
        return success_response(message="Success", data=serializer.data, status_code=status.HTTP_200_OK)

class GetAdminDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id=None, format=None):
        subadmin_list = User.objects.filter(id=id).first()
        serializer = AdminProfileDetailSerializer(subadmin_list)
        return success_response(message="Success", data=serializer.data, status_code=status.HTTP_200_OK)


class StudentProfileImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, id=None, format=None):
        subadmin_list = User.objects.filter(role = User.Student, id=id).first()
        if subadmin_list:
            serializer = StudentProfileImageUploadSerializer(subadmin_list, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return success_response(message="Success", data=serializer.data, status_code=status.HTTP_200_OK)
            return error_response(message="failed", data = serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        else:
            return error_response(message="failed", data = {}, status_code=status.HTTP_400_BAD_REQUEST)


class CheckEmail(APIView):
    def post(self, request, format=None):
        email = request.data.get("email")

        if not email:
            return error_response(
                message="Email is required",
                data={},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return success_response(
                message="Email exists",
                data={"isExist":True},
                status_code=status.HTTP_200_OK
            )

        return success_response(
            message="Email not found",
            data={"isExist":False},
            status_code=status.HTTP_200_OK
        )


class MediaAccessUrlView(APIView):
    def post(self, request, format=None):
        gcs_file = request.data.get("url")
        bucket = client.bucket(settings.GS_BUCKET_NAME_2)
        blob = bucket.blob(gcs_file)
        # blob.upload_from_filename(pdf_path, content_type="application/pdf")
        # ---------- Generate signed URL ----------
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=settings.SIGNED_URL_EXPIRY),
            method="GET"
        )
        return success_response(message="Success", data=[{"url":url}], status_code=status.HTTP_200_OK)


def send_email_async(subject, message, email_from, recipient_list, html_message):
    print("start calling")
    send_mail(
        subject,
        message,
        email_from,
        recipient_list,
        html_message=html_message,
        fail_silently=False
    )
    print("end calling")

class Mail_test(APIView):
    def post(self, request, format=None):
        subject = 'Test Email'
        message = 'This is a test email from Django application.'
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = ['vishal.dubey@kcglobed.com']
        html_message = ''
        # fail_silently=False
        threading.Thread(
            target=send_email_async,
            args=(subject, message, email_from, recipient_list, html_message)
        ).start()
       
        
        return success_response(message="Success", data=[], status_code=status.HTTP_200_OK)




import requests
from requests.auth import HTTPBasicAuth

ACCOUNT_ID = "PxicTngdTxewxGNCZ69ANQ"
CLIENT_ID = "WH6b4ExrS4KO145mbyNjPw"
CLIENT_SECRET = "sxA2YPgF8swXKSp4ORNAJS8Wpppig4AE"

class Zoom_test(APIView):
    def post(self, request, format=None):
        

        url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ACCOUNT_ID}"

        response = requests.post(
            url,
            auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
        )
        print(response)
        access_token = response.json()["access_token"]
        return success_response(message="Success", data=[access_token], status_code=status.HTTP_200_OK)


import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings


class ZoomService:

    @staticmethod
    def get_access_token():
        url = (
            "https://zoom.us/oauth/token"
            f"?grant_type=account_credentials&account_id={settings.ZOOM_ACCOUNT_ID}"
        )

        response = requests.post(
            url,
            auth=HTTPBasicAuth(
                settings.ZOOM_CLIENT_ID,
                settings.ZOOM_CLIENT_SECRET
            )
        )

        response.raise_for_status()
        return response.json()["access_token"]

    @staticmethod
    def create_meeting(topic, start_time, duration=30):
        token = ZoomService.get_access_token()

        url = "https://api.zoom.us/v2/users/me/meetings"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "topic": topic,
            "type": 2,
            "start_time": start_time,      # ISO format
            "duration": duration,
            "timezone": "Asia/Kolkata",
            "agenda": "Interview Discussion",
            "settings": {
                "host_video": True,
                "participant_video": True,
                "join_before_host": False,
                "waiting_room": True,
                "approval_type": 0,
            },
        }

        response = requests.post(url, json=payload, headers=headers)

        print(response.status_code)
        print(response.text)   # <-- Important

        response.raise_for_status()

        return response.json()



class CreateZoomMeetingAPIView(APIView):

    def post(self, request):
        topic = request.data.get("topic")
        start_time = request.data.get("start_time")
        duration = request.data.get("duration", 30)

        meeting = ZoomService.create_meeting(
            topic=topic,
            start_time=start_time,
            duration=duration
        )

        return Response({
            "status": True,
            "message": "Meeting created successfully",
            "data": {
                "meeting_id": meeting["id"],
                "password": meeting["password"],
                "join_url": meeting["join_url"],
                "start_url": meeting["start_url"],
                "start_time": meeting["start_time"],
            }
        })


    