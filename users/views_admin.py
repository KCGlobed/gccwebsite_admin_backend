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
        statuss = False
        if ManageFreeReferal.objects.filter(free_referral_code=code).exists():
                statuss = True
                return success_response(message="success", data={"verified_status":statuss}, status_code=status.HTTP_200_OK)
        if User.objects.filter(referral_code=code).exists():
            user_obj = User.objects.filter(referred_code=code)
            if not user_obj:
                statuss = True
                return success_response(message="success", data={"verified_status":statuss}, status_code=status.HTTP_200_OK)
        return error_response(message="Invalid Code", data = {"verified_status":statuss}, status_code=status.HTTP_400_BAD_REQUEST)
    


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

from gcc_backend.utils import get_lower_reporting

class GetLowerReportingPerson(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        data = get_lower_reporting(5545)
        users_data = User.objects.filter(id__in=data).values("id","first_name","last_name","email","role")

        return success_response(message="Success", data={"list_data":users_data}, status_code=status.HTTP_200_OK)

class GetUpperReportingPerson(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        data = get_upper_reporting(5548)
        users_data = User.objects.filter(id__in=data).values("id","first_name","last_name","email","role")

        return success_response(message="Success", data={"list_data":users_data}, status_code=status.HTTP_200_OK)
    



class GetManageSalesPerson(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        users_data = User.objects.filter(role=User.SalesPerson).values("id","first_name","last_name","email","role")

        return success_response(message="Success", data={"list_data":users_data}, status_code=status.HTTP_200_OK)
    



