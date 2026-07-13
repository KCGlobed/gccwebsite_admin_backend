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
import pandas as pd
import tempfile
import re
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date
client = storage.Client(project=settings.GS_PROJECT_ID)
from django.db.models import F, FloatField, ExpressionWrapper
from django.db.models.functions import Cast

from openpyxl import load_workbook





## excel report data include
def get_student_score_card_url(oid):
    std_data = StudentProfile.objects.filter(id=oid).first()
    score_objs = StudentRealExamResult.objects.filter(student_profile=std_data).last()
    if not score_objs:
        return ""
        
    datas = []
    for i in score_objs.json_data:
        obj = {}
        obj["Name"] = i["Name"]
        obj["TotalQuestions"] = i["TotalQuestions"]
        obj["Incorrect"] = int(float(i["Attempted"])-float(i['Correct']))
        obj["Correct"] = i["Correct"]
        obj["NotAttempted"] = int(float(i["TotalQuestions"]) - float(i["Attempted"]))
        datas.append(obj)

    static_selected_bucket = settings.GS_BUCKET_NAME
    context = {
        "candidate_name":f"{std_data.first_name.upper()} {std_data.last_name.upper()}",
        "application_id":std_data.application_id,
        "date_of_exam":std_data.slot_date,
        "time_of_exam":std_data.slot_time,
        "sections":datas,
        "total_questions":score_objs.totalquestions,
        "total_correct":score_objs.totalcorrectanswers,
        "total_incorrect":int(float(score_objs.totalquestionsattempted) - float(score_objs.totalcorrectanswers)),
        "total_not_attempted":int(float(score_objs.totalquestions) - float(score_objs.totalquestionsattempted)),

        "username": std_data.email,
        "user_id": std_data.id,
        "application_id": std_data.application_id,
        "student_name": f'''{std_data.first_name.upper()}" "{std_data.last_name.upper()}''',
        "slot_date": std_data.slot_date,
        "slot_time": std_data.slot_time,
        "photo": std_data.photo.url,
        "signature": std_data.signature.url,
        "barcode":"",
        "report_date": datetime.now(),
        # "test_link":"https://cocubes.in/gccschool-nfet",
        "test_link":"https://www.gccschool.com/myaccount",
        "bucket_static_logo":f"https://storage.googleapis.com/{static_selected_bucket}/static/images/gcc-admit-card-logo.jpeg",
        # "bucket_static_signature":f"https://storage.googleapis.com/{static_selected_bucket}/static/images/admit_card_signature.png"
        "bucket_static_signature":f"https://storage.googleapis.com/{static_selected_bucket}/static/images/gcc_admit_card_sign.png"
    }
    
    # Render template
    template = get_template("pdf/student_score_card.html")
    html = template.render(context)

    # xhtml2pdf needs ISO-8859-1
    html = html.encode("ISO-8859-1", "ignore").decode("ISO-8859-1")

    # Create temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_path = tmp.name
        pisa_status = pisa.CreatePDF(BytesIO(html.encode("ISO-8859-1")), dest=tmp)

    if pisa_status.err:
        os.remove(pdf_path)
        return ""
    try:
        # Upload to GCS
        username = re.sub(r"\s+", "_", std_data.email)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        gcs_file = f"media/admit_card/{username}_{std_data.id}.pdf"

        bucket = client.bucket(settings.GS_BUCKET_NAME)
        blob = bucket.blob(gcs_file)
        blob.upload_from_filename(pdf_path, content_type="application/pdf")
        # ---------- Generate signed URL ----------
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=settings.SIGNED_URL_EXPIRY),
            method="GET"
        )
        return url

    finally:
        os.remove(pdf_path)