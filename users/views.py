from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from gcc_backend.utils import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated

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


                return success_response(message="Login Success", data={'token': token, 'user_role': serializer.data.get('role'), "user_id":user.id}, status_code=status.HTTP_200_OK)
            else:
                return error_response(message="failed", data = {}, status_code=status.HTTP_400_BAD_REQUEST)
        
        return error_response(message="failed", data = serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    



class CreateStudentView(APIView):
    def post(self, request, format=None):
        serializer = CreateStudentSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            user  = serializer.save()
            return success_response(message="User Created Successfully", data={}, status_code=status.HTTP_200_OK)
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
    def get(self, request, id=None,format=None):
        subadmin_list = User.objects.filter(role = User.Student, id=id).first()
        serializer = StudentProfileSerializer(subadmin_list)
        return success_response(message="Success", data=serializer.data, status_code=status.HTTP_200_OK)
    