from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework import filters
from gcc_backend.pagination import CustomPageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import get_template
from google.cloud import storage
import os
from gcc_backend.utils import *
import pandas as pd
import tempfile
import re
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date
client = storage.Client(project=settings.GS_PROJECT_ID)
import io
from openpyxl import Workbook
from django.core.mail import EmailMessage
from django.utils.timezone import now
from rest_framework import status
from django.utils import timezone
from datetime import timedelta




class CampusStudentVerifiedStatusView(APIView):
    def post(self, request, format=None):
        if request.data.get("status") is None or request.data.get("id") is None:
            return error_response(message="failed", data = {"error":"Invalid request"}, status_code=status.HTTP_400_BAD_REQUEST)
        campus_std = CampusStudent.objects.filter(id=request.data.get("id")).first()
        serializer = CampusStudentVerifiedStatusSerializer(campus_std, data = request.data)
        if serializer.is_valid(raise_exception = True):
            serializer.save()
            return success_response(message="User Verified Successfully", data={}, status_code=status.HTTP_200_OK)
        return error_response(message="failed", data = serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    


class CampusStudentAccountMailStatusView(APIView):
    def post(self, request, format=None):
        if request.data.get("status") is None or request.data.get("id") is None:
            return error_response(message="failed", data = {"error":"Invalid request"}, status_code=status.HTTP_400_BAD_REQUEST)
        campus_std = CampusStudent.objects.filter(id=request.data.get("id")).first()
        serializer = CampusStudentAccountEmailStatusSerializer(campus_std, data = request.data, partial=True)
        if serializer.is_valid(raise_exception = True):
            serializer.save()
            return success_response(message="Mail Sent Successfully", data={}, status_code=status.HTTP_200_OK)
        return error_response(message="failed", data = serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    


class ReAttemptPaymentsView(APIView):
    def post(self, request, format=None):
        data = Payments.objects.filter(dossier_form=None)
        print("data listing.....",len(data))
        # for i in data:
        #     # print(i)
        #     print(i.response)
        #     email = i.response["email"]
        #     phone = i.response["mobile"]
        #     lead = DossierData.objects.filter(email=email, phone=phone)
        #     print(lead)
        #     if lead:
        #         print(len(lead))
        #         print(email)
        #         print(phone)
        #         print(i.amount)
        #         ll = lead.first()
        #         i.dossier_form = ll
        #         i.form_id = ll.id
        #         i.re_attempt_status = True
        #         i.save()
                
        return success_response(message="Success", data={}, status_code=status.HTTP_200_OK)
    


class MerittoExamResultUpdateView(APIView):
    def post(self, request, format=None):
        std_objs = StudentRealExamResult.objects.all()
        print("data listing.....",len(std_objs))
        for std_profile in std_objs:
        # if std_objs:
            # std_profile = std_objs.last()
            total_score = str(round((float(std_profile.totalscore) / float(std_profile.totalquestions)) * 100, 2))
            
            if settings.MERITO_STATUS == "True":
                url = settings.MERITO_BASE_URL+"/application/v1/createOrUpdate"

                headers = {
                        "Content-Type": "application/json",
                        "secret-key": settings.MERITO_SECRETE_KEY,
                        "access-key": settings.MERITO_ACCESS_KEY
                    }
                meritto_payload = {
                    "form_id": 22144,
                    "email": std_profile.student_profile.email,
                    "search_criteria":"email",
                    "data": {
                            "field_349944":total_score
                    }
                }
                print(meritto_payload)
                try:
                    response = requests.post(url, headers=headers, json=meritto_payload)
                    print(response.status_code)
                    print(response.text)
                except Exception as e:
                    print("API Error:", str(e))
        return success_response(message="Success", data={}, status_code=status.HTTP_200_OK)
    





