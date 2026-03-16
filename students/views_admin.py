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
        serializer = CampusStudentVerifiedStatusSerializer(campus_std, data = request.data, partial=True)
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
    

