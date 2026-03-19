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


class CareerApplication_list(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id']
    ordering_fields = ['id']
    def get(self, request):
        datas = CareerApplication.objects.all().order_by('-id')

        # Date range filter
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                datas = datas.filter(created_at__date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                datas = datas.filter(created_at__date__lte=end_date)

        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(datas, request, view=self)
        serializers = ListCareerApplicationSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    

class PartnerWithUs_list(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id']
    ordering_fields = ['id']
    def get(self, request):
        datas = PartnerWithUs.objects.all().order_by('-id')

        # Date range filter
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                datas = datas.filter(created_at__date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                datas = datas.filter(created_at__date__lte=end_date)


        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(datas, request, view=self)
        serializers = ListPartnerWithUsSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    

class DossierDataForm_Create(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = CreateDossierDataSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            obj = serializer.save()
            pdf_url = f"{settings.STATIC_URL}files/GCC%20SCHOOL%20Dossier.pdf"
            return success_response(message="success", data={"url":pdf_url, "id":obj.id, "data":ListDossierDataSerializer(obj).data}, status_code=status.HTTP_200_OK)
        else:
            return error_response(message="failed", data = {}, status_code=status.HTTP_400_BAD_REQUEST)



class DossierDataForm_List(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"full_name","email","phone","city","state"]
    ordering_fields = ['id',"full_name","email","phone","city","state","created_at"]
    def get(self, request):
        datas = DossierData.objects.filter(source=SourceType.Website).order_by('-id')

        full_name = request.GET.get('full_name')
        if full_name:
            datas = datas.filter(full_name__icontains=full_name)

        email = request.GET.get('email')
        if email:
            datas = datas.filter(email__icontains=email)


        phone = request.GET.get('phone')
        if phone:
            datas = datas.filter(phone__icontains=phone)


        state = request.GET.get('state')
        if state:
            datas = datas.filter(state__icontains=state)

        city = request.GET.get('city')
        if city:
            datas = datas.filter(city__icontains=city)

        # Date range filter
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                datas = datas.filter(created_at__date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                datas = datas.filter(created_at__date__lte=end_date)


        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(datas, request, view=self)
        serializers = ListDossierDataSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    

class DossierDataEfosForm_List(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"full_name","email","phone","city","state"]
    ordering_fields = ['id',"full_name","email","phone","city","state","created_at"]
    def get(self, request):
        datas = DossierData.objects.filter(source=SourceType.Efos).order_by('-id')

        full_name = request.GET.get('full_name')
        if full_name:
            datas = datas.filter(full_name__icontains=full_name)

        email = request.GET.get('email')
        if email:
            datas = datas.filter(email__icontains=email)


        phone = request.GET.get('phone')
        if phone:
            datas = datas.filter(phone__icontains=phone)


        state = request.GET.get('state')
        if state:
            datas = datas.filter(state__icontains=state)

        city = request.GET.get('city')
        if city:
            datas = datas.filter(city__icontains=city)

        # Date range filter
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                datas = datas.filter(created_at__date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                datas = datas.filter(created_at__date__lte=end_date)


        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(datas, request, view=self)
        serializers = ListDossierDataSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    

class NewsletterSubscribers_List(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id']
    ordering_fields = ['id']
    def get(self, request):
        datas = NewsletterSubscribers.objects.all().order_by('-id')

        # Date range filter
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                datas = datas.filter(created_at__date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                datas = datas.filter(created_at__date__lte=end_date)

        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(datas, request, view=self)
        serializers = ListNewsletterSubscriberSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    


class CreateSupportFormView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = CreateSupportFormSerializer(data = request.data, context={'request': request})
        if serializer.is_valid(raise_exception = True):
            obj = serializer.save()
            subject = f'Feedback - {obj.subject}'
            message = obj.message
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = ['info@gccschool.com','support@gccschool.com']
            # html_message = ""
            html_message = loader.render_to_string(
                    'feedback_mail.html',
                    {
                        "full_name":obj.user.first_name,
                        "email":obj.user.email,
                        "application_id":obj.user.application_id,
                        "subject":obj.subject,
                        "message":obj.message,
                        "created_at":obj.created_at
                    }
                )
            threading.Thread(
                target=send_email_async,
                args=(subject, message, email_from, recipient_list, html_message)
            ).start()
            return success_response(message="success", data={"id":obj.id, "data":CreateSupportFormSerializer(obj).data}, status_code=status.HTTP_200_OK)
        else:
            return error_response(message="failed", data = {}, status_code=status.HTTP_400_BAD_REQUEST)


class SupportForm_page_list(APIView):
    # permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id']
    ordering_fields = ['id']
    def get(self, request):
        datas = SupportForm.objects.all().order_by('-id')

        # Date range filter
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                datas = datas.filter(created_at__date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                datas = datas.filter(created_at__date__lte=end_date)


        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(datas, request, view=self)
        serializers = ListSupportFormSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    


class GetDossierReportPDFView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"full_name","email","phone","city","state"]
    ordering_fields = ['id',"full_name","email","phone","city","state","created_at"]
    def get(self, request, sid=None):
        
        datas = DossierData.objects.filter(source=SourceType.Website).order_by('-id')

        full_name = request.GET.get('full_name')
        if full_name:
            datas = datas.filter(full_name__icontains=full_name)

        email = request.GET.get('email')
        if email:
            datas = datas.filter(email__icontains=email)


        phone = request.GET.get('phone')
        if phone:
            datas = datas.filter(phone__icontains=phone)


        state = request.GET.get('state')
        if state:
            datas = datas.filter(state__icontains=state)

        city = request.GET.get('city')
        if city:
            datas = datas.filter(city__icontains=city)

        # Date range filter
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                datas = datas.filter(created_at__date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                datas = datas.filter(created_at__date__lte=end_date)


        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        serializers = ListDossierDataSerializer(datas, many=True)


        data = {
                    "user_data":serializers.data,
                    "report_date": datetime.now().strftime("%d-%m-%Y, %H:%M")
                }
        

        template = get_template('pdf/dossier_report.html')
        html  = template.render(data)
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            pdf_path = temp_file.name
            
            # Encode HTML and create PDF
            html = html.encode('latin-1', 'replace').decode('latin-1')
            pdf = pisa.CreatePDF(BytesIO(html.encode("ISO-8859-1")), dest=temp_file)

            if pdf.err:
                raise Exception("PDF generation error!")
        
        # After the 'with' block, the file is closed, but not deleted yet
        try:
            # GCS file naming logic
            timestamp = datetime.now().strftime("%d_%m_%y_%H_%M")
            report_name = "dossier_report"
            gcs_folder_name = "media/gcc/reports"
            gcs_file_name = f"{gcs_folder_name}/{report_name}_{timestamp}.pdf"

            # Upload the temporary file to GCS
            bucket = client.get_bucket(settings.GS_BUCKET_NAME)
            blob = bucket.blob(gcs_file_name)
            blob.upload_from_filename(pdf_path)

            return success_response(
                message="Success",
                data={"report_url": blob.public_url},
                status_code=status.HTTP_200_OK
            )
        finally:
            # Ensure the temporary file is deleted from the server's disk
            os.remove(pdf_path)
    


class GetDossierReportExcelView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"full_name","email","phone","city","state"]
    ordering_fields = ['id',"full_name","email","phone","city","state","created_at"]

    def get(self, request, sid=None):
        
        datas = DossierData.objects.filter(source=SourceType.Website).order_by('-id')

        full_name = request.GET.get('full_name')
        if full_name:
            datas = datas.filter(full_name__icontains=full_name)

        email = request.GET.get('email')
        if email:
            datas = datas.filter(email__icontains=email)


        phone = request.GET.get('phone')
        if phone:
            datas = datas.filter(phone__icontains=phone)


        state = request.GET.get('state')
        if state:
            datas = datas.filter(state__icontains=state)

        city = request.GET.get('city')
        if city:
            datas = datas.filter(city__icontains=city)

        # Date range filter
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                datas = datas.filter(created_at__date__gte=start_date)

        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                datas = datas.filter(created_at__date__lte=end_date)


        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        serializers = ListDossierDataSerializer(datas, many=True)

        lis = []
        
        lis.append({
                "name":"Dossier Report",
                "email":'',
                "subject":'',
                "Chapter":'',
                "Topic":'',
                "total_questions":''
            })

       
        lis.append({
                "name":"",
                "email":'',
                "subject":'',
                "Chapter":'',
                "Topic":'',
                "total_questions":''
            })
        
        lis.append({
                "name":"Full Name",
                "email":'Email',
                "subject":'Phone Number',
                "Chapter":'City',
                "Topic":'State',
                "total_questions":'Created At',
            })
        
        
        for chapter_data in serializers.data:
            lis.append({
                "name":chapter_data['full_name'],
                "email":chapter_data['email'],
                "subject":chapter_data['phone'],
                "Chapter":chapter_data['city'],
                "Topic":chapter_data['state'],
                "total_questions":chapter_data['created_at'],
            })


        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            pdf_path = temp_file.name
            
            # Create DataFrame and save to the temporary file
            df = pd.DataFrame.from_dict(lis)
            df.to_excel(pdf_path, header=False, index=False)
        
        # After the 'with' block, the file is closed but not deleted
        try:
            # GCS file naming logic
            timestamp = datetime.now().strftime("%d_%m_%y_%H_%M")
            report_name = "dossier_report"
            gcs_folder_name = "media/gcc/reports"
            gcs_file_name = f"{gcs_folder_name}/{report_name}_{timestamp}.xlsx"

            # Upload the temporary file to GCS
            bucket = client.get_bucket(settings.GS_BUCKET_NAME)
            blob = bucket.blob(gcs_file_name)
            blob.upload_from_filename(pdf_path)

            return success_response(
                message="Success",
                data={"report_url": blob.public_url},
                status_code=status.HTTP_200_OK
            )
        finally:
            # Ensure the temporary file is deleted
            os.remove(pdf_path)