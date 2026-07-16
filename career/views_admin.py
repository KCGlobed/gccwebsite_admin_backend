from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework import filters
from gcc_backend.pagination import CustomPageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from gcc_backend.utils import *
from gcc_backend import settings
from google.cloud import storage
import pandas as pd
import tempfile
import re
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date
client = storage.Client(project=settings.GS_PROJECT_ID)
import os

from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import get_template

from gcc_backend.utils import send_email_async
import threading
from django.conf import settings
from django.db.models import OuterRef, Exists

from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment

from students.models import *
from datetime import date, timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate




class GetDossierDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id):
        datas = DossierData.objects.filter(id=id).first()
        serialize_data = DossierDetailSerializer(datas).data
        return success_response(message="success", data={"data":serialize_data}, status_code=status.HTTP_200_OK)

    


