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
import io
from openpyxl import Workbook
from django.core.mail import EmailMessage
from django.utils.timezone import now
from rest_framework import status
from django.utils import timezone
from datetime import timedelta



# Create your views here.

class StudentQuery_list(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id']
    ordering_fields = ['id']
    def get(self, request):
        datas = StudentEnquiries.objects.all().order_by('-id')

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
        serializers = ListStudentDataSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    


class StudentPayment_list(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"razorpay_order_id","razorpay_payment_id","amount","dossier_form__full_name","dossier_form__email","dossier_form__phone","dossier_form__state","dossier_form__city"]
    ordering_fields = ['id',"created_at","dossier_form__full_name","dossier_form__email","dossier_form__phone","dossier_form__state","dossier_form__city","razorpay_order_id","razorpay_payment_id","amount"]
    def get(self, request):

        datas = Payments.objects.all().order_by('-id')

        full_name = request.GET.get('full_name')
        if full_name:
            datas = datas.filter(dossier_form__full_name__icontains=full_name)

        email = request.GET.get('email')
        if email:
            datas = datas.filter(dossier_form__email__icontains=email)


        phone = request.GET.get('phone')
        if phone:
            datas = datas.filter(dossier_form__phone__icontains=phone)


        state = request.GET.get('state')
        if state:
            datas = datas.filter(dossier_form__state__icontains=state)

        city = request.GET.get('city')
        if city:
            datas = datas.filter(dossier_form__city__icontains=city)

        city = request.GET.get('city')
        if city:
            datas = datas.filter(dossier_form__city__icontains=city)
        
        # Date range filter
        start_date = request.GET.get('start_date')
        end_date   = request.GET.get('end_date')
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
        serializers = ListStudentPaymentSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    




class ExportPaymentExcelView(APIView):
    def get(self, request):
        recipient_email = "testtechno0@yopmail.com"
        # 1. Fetch data (Reuse your annotated logic)
        # Note: Using .iterator() is better for large datasets to save memory
        
        # 1. Calculate the timestamp for 24 hours ago
        time_threshold = timezone.now() - timedelta(hours=24)

        # 2. Filter queryset
        # Note: 'isnull' is lowercase in Django lookups
        queryset = Payments.objects.filter(
            razorpay_order_id__isnull=False,
            created_at__gte=time_threshold
        ).order_by('-created_at')
        # 2. Create Excel in memory
        wb = Workbook()
        ws = wb.active
        ws.title = "Payments Report"

        # Headers
        headers = ['Order ID','Payment ID', 'Amount', 'Currency', 'Student Name', 'Email', "Phone","City","State","Payment Status",'Date']
        ws.append(headers)

        # Rows
        for p in queryset:

            dossier = p.dossier_form

            ws.append([
                p.razorpay_order_id,
                p.razorpay_payment_id,
                float(p.amount),
                p.currency,
                dossier.full_name if dossier else "N/A",
                dossier.email if dossier else "N/A",
                dossier.phone if dossier else "N/A",
                dossier.city if dossier else "N/A",
                dossier.state if dossier else "N/A",
                p.status,
                p.created_at.strftime('%Y-%m-%d %H:%M') if p.created_at else "N/A"
            ])

        # Save to BytesIO stream
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)


        queryset1 = DossierData.objects.filter(
            created_at__gte=time_threshold
        ).order_by('-created_at')
        # 2. Create Excel in memory
        wb1 = Workbook()
        ws1 = wb1.active
        ws1.title = "Dossior Lead Report"

        # Headers
        headers = ['Student Name', 'Email', "Phone","City","State",'Date']
        ws1.append(headers)

        # Rows
        for dossier in queryset1:

            ws1.append([
                dossier.full_name if dossier else "N/A",
                dossier.email if dossier else "N/A",
                dossier.phone if dossier else "N/A",
                dossier.city if dossier else "N/A",
                dossier.state if dossier else "N/A",
                p.created_at.strftime('%Y-%m-%d %H:%M') if p.created_at else "N/A"
            ])

        # Save to BytesIO stream
        output1 = io.BytesIO()
        wb1.save(output1)
        output1.seek(0)

        # 3. Send Email
        try:
            subject = f"Payment Report & Dossier Lead - {now().strftime('%d %b %Y')}"

            bcc_list = ['testtechno0@yopmail.com']
            # Corrected the slashes to backslashes for proper line breaks
            message = (
                "Hello Sir,\n\n"
                "Please find the attached payment report & dossier lead report for the last 24 hours.\n\n"
                "Thanks,\n"
                "KCGlobed Team"
            )
            email = EmailMessage(
                subject,
                message,
                'kamalchhabra@kcglobed.com',
                [recipient_email],
                bcc=bcc_list,
            )
            
            # Attach the file (filename, content, mimetype)
            email.attach(
                f'Payment_Report_{now().strftime("%Y%m%d")}.xlsx',
                output.getvalue(),
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

            email.attach(
                f'Dossier_Report_{now().strftime("%Y%m%d")}.xlsx',
                output1.getvalue(),
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            email.send()

            return Response({"message": "Email sent successfully"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CampusFaculty_list(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id']
    ordering_fields = ['id']
    def get(self, request):
        datas = CampusFaculty.objects.all().order_by('-id')

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
        serializers = ListCampusFacultySerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    

class CampusStudent_list(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id']
    ordering_fields = ['id']
    def get(self, request):
        datas = CampusStudent.objects.all().order_by('-id')

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
        serializers = ListCampusStudentSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    



class ContactUsView(APIView):
    def post(self, request, format=None):
        serializer = ContactUsSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            user  = serializer.save()
            return Response({'message':'Message sent Successfully','data':serializer.data})

        return Response(serializer.errors)
    

class GetContactUSView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name',"last_name","email","phone","state","city"]
    ordering_fields = ['first_name',"last_name","email","phone","state","city","created_at"]
    def get(self, request):
        datas = ContactUs.objects.all()

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
        serializers = ContactListSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    


class CreateStudentProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = CompleteStudentSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            user  = serializer.save()
            return Response({'message':'Message sent Successfully','data':[]})

        return Response(serializer.errors)
    


class GetStudentProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        datas = StudentProfile.objects.filter(user = request.user).first()
        if datas is not None:
            serializers = StudentProfileSerializer(datas)
            return Response({'message':'','data':serializers.data})

        return Response({'message':'','data':[]})