from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from gcc_backend.utils import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated



class CreateUniversityStudentView(APIView):
    def post(self, request, format=None):
        serializer = CreateUniversityStudentSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            user  = serializer.save()
            # generated_password = serializer.generated_password
            return success_response(message="User Created Successfully", data={}, status_code=status.HTTP_200_OK)
        return error_response(message="failed", data = serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    




class VerifyRefferalCodeView(APIView):
    def post(self, request, format=None):
        code = request.data.get('refferal_code')
        if User.objects.filter(referral_code=code).exists():
            user_obj = User.objects.filter(referred_code=code)
            statuss = False
            if not user_obj:
                statuss = True
                return success_response(message="success", data={"status":statuss}, status_code=status.HTTP_200_OK)
        return error_response(message="failed", data = {"status":statuss}, status_code=status.HTTP_400_BAD_REQUEST)
    


import random
import string
def generate_referral_code():
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=20))





class CreateStudentRefferalCodeView(APIView):
    def post(self, request, format=None):
        user = User.objects.all()
        for i in user:
            data = generate_referral_code()
            user_data = User.objects.filter(referral_code=data)
            if len(user_data) == 0 and not i.referral_code:
                i.referral_code = data
                i.save()
        return success_response(message="User Created Successfully", data={}, status_code=status.HTTP_200_OK)