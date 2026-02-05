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
client = storage.Client(project=settings.GS_PROJECT_ID)



# Create your views here.

class StudentQuery_list(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id']
    ordering_fields = ['id']
    def get(self, request):
        datas = StudentEnquiries.objects.all().order_by('-id')
        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(datas, request, view=self)
        serializers = ListStudentQuerySerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    


class StudentData_list(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id']
    ordering_fields = ['id']
    def get(self, request):
        datas = StudentsData.objects.all().order_by('-id')
        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(datas, request, view=self)
        serializers = ListStudentDataSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    


class StudentPayment_list(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id']
    ordering_fields = ['id']
    def get(self, request):
        datas = Payments.objects.all().order_by('-id')
        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(datas, request, view=self)
        serializers = ListStudentPaymentSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    



class CampusFaculty_list(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id']
    ordering_fields = ['id']
    def get(self, request):
        datas = CampusFaculty.objects.all().order_by('-id')
        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(datas, request, view=self)
        serializers = ListCampusFacultySerializer(page, many=True)
        print(serializers)
        
        return paginator.get_paginated_response(serializers.data)
    

class CampusStudent_list(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id']
    ordering_fields = ['id']
    def get(self, request):
        datas = CampusStudent.objects.all().order_by('-id')
        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(datas, request, view=self)
        serializers = ListCampusStudentSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    




class GetSessionReportPDFView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        data_objs = CampusStudent.objects.all().order_by("-id")
        data_list = CampusStudentPDFSerializer(data_objs, many=True).data

        context = {
            "username": request.user.email,
            "user_id": request.user.id,
            "data_list": data_list,
            "report_date": datetime.now()
        }

        # Render template
        template = get_template("pdf/session_report.html")
        html = template.render(context)

        # xhtml2pdf needs ISO-8859-1
        html = html.encode("ISO-8859-1", "ignore").decode("ISO-8859-1")

        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf_path = tmp.name
            pisa_status = pisa.CreatePDF(BytesIO(html.encode("ISO-8859-1")), dest=tmp)

        if pisa_status.err:
            os.remove(pdf_path)
            return Response({"error": "PDF generation failed"}, status=500)

        try:
            # Upload to GCS
            username = re.sub(r"\s+", "_", request.user.email)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            gcs_file = f"media/kcc_data_list/reports/{username}_{timestamp}.pdf"

            bucket = client.bucket(settings.GS_BUCKET_NAME)
            blob = bucket.blob(gcs_file)
            blob.upload_from_filename(pdf_path, content_type="application/pdf")
            # ---------- Generate signed URL ----------
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=1),
                method="GET"
            )
            return Response({
                "message": "Success",
                "data": {
                    "report_url": url
                }
            })

        finally:
            os.remove(pdf_path)
