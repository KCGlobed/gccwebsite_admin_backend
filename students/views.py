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
    search_fields = ['id',"razorpay_order_id","razorpay_payment_id","amount","dossier_form__full_name","dossier_form__email","dossier_form__phone","dossier_form__state","dossier_form__city","status"]
    ordering_fields = ['id',"created_at","dossier_form__full_name","dossier_form__email","dossier_form__phone","dossier_form__state","dossier_form__city","razorpay_order_id","razorpay_payment_id","amount"]
    def get(self, request):

        datas = Payments.objects.filter(source=SourceType.Website).order_by('-id')

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

        status = request.GET.get('status')
        if status:
            datas = datas.filter(status__icontains=status)

        
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
    

class StudentSourcePayment_list(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"razorpay_order_id","razorpay_payment_id","amount","dossier_form__full_name","dossier_form__email","dossier_form__phone","dossier_form__state","dossier_form__city","status"]
    ordering_fields = ['id',"created_at","dossier_form__full_name","dossier_form__email","dossier_form__phone","dossier_form__state","dossier_form__city","razorpay_order_id","razorpay_payment_id","amount"]
    def get(self, request):
        source_type = request.GET.get("source")
        if source_type:
            datas = Payments.objects.filter(source=source_type).order_by('-id')
        else:
            datas = Payments.objects.filter(source=SourceType.Website).order_by('-id')

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

        status = request.GET.get('status')
        if status:
            datas = datas.filter(status__icontains=status)

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
                dossier.created_at.strftime('%Y-%m-%d %H:%M') if dossier.created_at else "N/A"
            ])

        # Save to BytesIO stream
        output1 = io.BytesIO()
        wb1.save(output1)
        output1.seek(0)


        queryset2 = ContactUs.objects.filter(
            created_at__gte=time_threshold
        ).order_by('-created_at')
        # 2. Create Excel in memory
        wb2 = Workbook()
        ws2 = wb2.active
        ws2.title = "Contact Us Report"

        # Headers
        headers = ['First Name','Last Name', 'Email', "Phone","City","State",'Date']
        ws2.append(headers)

        # Rows
        for dossier in queryset2:

            ws2.append([
                dossier.first_name if dossier else "N/A",
                dossier.last_name if dossier else "N/A",
                dossier.email if dossier else "N/A",
                dossier.phone if dossier else "N/A",
                dossier.city if dossier else "N/A",
                dossier.state if dossier else "N/A",
                dossier.created_at.strftime('%Y-%m-%d %H:%M') if dossier.created_at else "N/A"
            ])

        # Save to BytesIO stream
        output2 = io.BytesIO()
        wb2.save(output2)
        output2.seek(0)

        # 3. Send Email
        try:
            subject = f"Payment Report, Dossier Lead & Contact Us - {now().strftime('%d %b %Y')}"

            bcc_list = ['atul.tevatia@kcglobed.com',"harish.kumar@kcglobed.com"]
            # Corrected the slashes to backslashes for proper line breaks
            message = (
                "Hello Sir,\n\n"
                "Please find the attached payment report , dossier lead report & Contact Us for the last 24 hours.\n\n"
                "Thanks,\n"
                "KCGlobed Team"
            )
            email = EmailMessage(
                subject,
                message,
                'info@gccschool.com',
                ["info@gccschoo.com","nfet@gccschool.com"],
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

            email.attach(
                f'Contact_Us_Report_{now().strftime("%Y%m%d")}.xlsx',
                output2.getvalue(),
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
    search_fields = ['full_name',"email","mobile","state","city"]
    ordering_fields = ["id",'full_name',"email","mobile","state","city","created_at"]
    def get(self, request):
        datas = CampusFaculty.objects.all().order_by('-id')

        full_name = request.GET.get('full_name')
        if full_name:
            datas = datas.filter(full_name__icontains=full_name)

        email = request.GET.get('email')
        if email:
            datas = datas.filter(email__icontains=email)


        mobile = request.GET.get('mobile')
        if mobile:
            datas = datas.filter(mobile__icontains=mobile)


        state = request.GET.get('state')
        if state:
            datas = datas.filter(state__icontains=state)

        city = request.GET.get('city')
        if city:
            datas = datas.filter(city__icontains=city)

        
        address = request.GET.get('address')
        if address:
            datas = datas.filter(address__icontains=address)

        institution_name = request.GET.get('institution_name')
        if institution_name:
            datas = datas.filter(institution_name__icontains=institution_name)


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


class GetFacultyCampusReportPDFView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name',"email","mobile","state","city"]
    ordering_fields = ["id",'full_name',"email","mobile","state","city","created_at"]
    def get(self, request):
        datas = CampusFaculty.objects.all().order_by('-id')

        full_name = request.GET.get('full_name')
        if full_name:
            datas = datas.filter(full_name__icontains=full_name)

        email = request.GET.get('email')
        if email:
            datas = datas.filter(email__icontains=email)


        mobile = request.GET.get('mobile')
        if mobile:
            datas = datas.filter(mobile__icontains=mobile)


        state = request.GET.get('state')
        if state:
            datas = datas.filter(state__icontains=state)

        city = request.GET.get('city')
        if city:
            datas = datas.filter(city__icontains=city)

        address = request.GET.get('address')
        if address:
            datas = datas.filter(address__icontains=address)

        institution_name = request.GET.get('institution_name')
        if institution_name:
            datas = datas.filter(institution_name__icontains=institution_name)

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

        serializers = ListCampusFacultySerializer(datas, many=True)

        data = {
                    "user_data":serializers.data,
                    "report_date": datetime.now().strftime("%d-%m-%Y, %H:%M")
                }
        

        template = get_template('pdf/faculty_campus_report.html')
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
            report_name = "faculty_campus_report"
            gcs_folder_name = "media/gcc_reports"
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
    


class GetFacultyCampusReportExcelView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name',"email","mobile","state","city"]
    ordering_fields = ["id",'full_name',"email","mobile","state","city","created_at"]
    def get(self, request):
        datas = CampusFaculty.objects.all().order_by('-id')

        full_name = request.GET.get('full_name')
        if full_name:
            datas = datas.filter(full_name__icontains=full_name)

        email = request.GET.get('email')
        if email:
            datas = datas.filter(email__icontains=email)


        mobile = request.GET.get('mobile')
        if mobile:
            datas = datas.filter(mobile__icontains=mobile)


        state = request.GET.get('state')
        if state:
            datas = datas.filter(state__icontains=state)

        city = request.GET.get('city')
        if city:
            datas = datas.filter(city__icontains=city)

        address = request.GET.get('address')
        if address:
            datas = datas.filter(address__icontains=address)

        institution_name = request.GET.get('institution_name')
        if institution_name:
            datas = datas.filter(institution_name__icontains=institution_name)
               
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

        serializers = ListCampusFacultySerializer(datas, many=True)

        lis = []
        
        lis.append({
                "name":"Faculty Campus Report",
                "email":'',
                "subject":'',
                "Chapter":'',
                "Topic":'',
                "total_questions":'',
                "institution_name":"",
                "department":"",
                "designation":"",
                "teaching_experience":"",
                "industrial_experience":"",
                "highest_qualification":"",
                "motivation":"",
                "support_activities":"",
                "student_reach":"",
                "created_at":""
            })

       
        lis.append({
                "name":"",
                "email":'',
                "subject":'',
                "Chapter":'',
                "Topic":'',
                "total_questions":'',
                "institution_name":"",
                "department":"",
                "designation":"",
                "teaching_experience":"",
                "industrial_experience":"",
                "highest_qualification":"",
                "motivation":"",
                "support_activities":"",
                "student_reach":"",
                "created_at":""
            })
        
        lis.append({
                "name":"Full Name",
                "email":'Email',
                "subject":'Phone Number',
                "Chapter":'City',
                "Topic":'State',
                "total_questions":'Address',
                "institution_name":"Institution Name",
                "department":"Department",
                "designation":"Designation",
                "teaching_experience":"Teaching Experience",
                "industrial_experience":"Industrial Experience",
                "highest_qualification":"Highest Qualification",
                "motivation":"Motivation",
                "support_activities":"Support Activities",
                "student_reach":"Student Reach",
                "created_at":"Created At"
            })
        
        
        for chapter_data in serializers.data:

            activities = chapter_data['support_activities']
            activities_str = ", ".join(map(str, activities)) if isinstance(activities, list) else str(activities)


            lis.append({
                "name":chapter_data['full_name'],
                "email":chapter_data['email'],
                "subject":chapter_data['mobile'],
                "Chapter":chapter_data['city'],
                "Topic":chapter_data['state'],
                "total_questions":chapter_data['address'],
                "institution_name":chapter_data['institution_name'],
                "department":chapter_data['department'],
                "designation":chapter_data['designation'],
                "teaching_experience":chapter_data['teaching_experience'],
                "industrial_experience":chapter_data['industrial_experience'],
                "highest_qualification":chapter_data['highest_qualification'],
                "motivation":chapter_data['motivation'],
                "support_activities":activities_str,
                "student_reach":chapter_data['student_reach'],
                "created_at":chapter_data['created_at']
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
            report_name = "faculty_campus_report"
            gcs_folder_name = "media/gcc_reports"
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


class CampusStudent_list(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name',"email","mobile","state","city"]
    ordering_fields = ["id",'full_name',"email","mobile","state","city","created_at"]
    def get(self, request):
        datas = CampusStudent.objects.all().order_by('-id')

        full_name = request.GET.get('full_name')
        if full_name:
            datas = datas.filter(full_name__icontains=full_name)

        email = request.GET.get('email')
        if email:
            datas = datas.filter(email__icontains=email)


        mobile = request.GET.get('mobile')
        if mobile:
            datas = datas.filter(mobile__icontains=mobile)


        state = request.GET.get('state')
        if state:
            datas = datas.filter(state__icontains=state)

        city = request.GET.get('city')
        if city:
            datas = datas.filter(city__icontains=city)

        address = request.GET.get('address')
        if address:
            datas = datas.filter(address__icontains=address)

        college_name = request.GET.get('college_name')
        if college_name:
            datas = datas.filter(college_name__icontains=college_name)

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
    


class GetStudentCampusReportPDFView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name',"email","mobile","state","city"]
    ordering_fields = ["id",'full_name',"email","mobile","state","city","created_at"]
    def get(self, request):
        datas = CampusStudent.objects.all().order_by('-id')

        full_name = request.GET.get('full_name')
        if full_name:
            datas = datas.filter(full_name__icontains=full_name)

        email = request.GET.get('email')
        if email:
            datas = datas.filter(email__icontains=email)


        mobile = request.GET.get('mobile')
        if mobile:
            datas = datas.filter(mobile__icontains=mobile)


        state = request.GET.get('state')
        if state:
            datas = datas.filter(state__icontains=state)

        city = request.GET.get('city')
        if city:
            datas = datas.filter(city__icontains=city)

        address = request.GET.get('address')
        if address:
            datas = datas.filter(address__icontains=address)

        college_name = request.GET.get('college_name')
        if college_name:
            datas = datas.filter(college_name__icontains=college_name)

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

        serializers = ListCampusStudentSerializer(datas, many=True)

        data = {
                    "user_data":serializers.data,
                    "report_date": datetime.now().strftime("%d-%m-%Y, %H:%M")
                }
        

        template = get_template('pdf/student_campus_report.html')
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
            report_name = "student_campus_report"
            gcs_folder_name = "media/gcc_reports"
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
    


class GetStudentCampusReportExcelView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name',"email","mobile","state","city"]
    ordering_fields = ["id",'full_name',"email","mobile","state","city","created_at"]
    def get(self, request):
        datas = CampusStudent.objects.all().order_by('-id')

        full_name = request.GET.get('full_name')
        if full_name:
            datas = datas.filter(full_name__icontains=full_name)

        email = request.GET.get('email')
        if email:
            datas = datas.filter(email__icontains=email)


        mobile = request.GET.get('mobile')
        if mobile:
            datas = datas.filter(mobile__icontains=mobile)


        state = request.GET.get('state')
        if state:
            datas = datas.filter(state__icontains=state)

        city = request.GET.get('city')
        if city:
            datas = datas.filter(city__icontains=city)

        address = request.GET.get('address')
        if address:
            datas = datas.filter(address__icontains=address)

        college_name = request.GET.get('college_name')
        if college_name:
            datas = datas.filter(college_name__icontains=college_name)

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

        serializers = ListCampusStudentSerializer(datas, many=True)

        lis = []
        
        lis.append({
                "name":"Student Campus Report",
                "email":'',
                "subject":'',
                "Chapter":'',
                "Topic":'',
                "total_questions":'',
                "institution_name":"",
                "department":"",
                "designation":"",
                "teaching_experience":"",
                "industrial_experience":"",
                "highest_qualification":"",
                "motivation":"",
                "support_activities":"",
                "student_reach":"",
                "created_at":""
            })

       
        lis.append({
                "name":"",
                "email":'',
                "subject":'',
                "Chapter":'',
                "Topic":'',
                "total_questions":'',
                "institution_name":"",
                "department":"",
                "designation":"",
                "teaching_experience":"",
                "industrial_experience":"",
                "highest_qualification":"",
                "motivation":"",
                "support_activities":"",
                "student_reach":"",
                "created_at":""
            })
        
        lis.append({
                "name":"Full Name",
                "email":'Email',
                "subject":'Phone Number',
                "Chapter":'City',
                "Topic":'State',
                "total_questions":'Address',
                "institution_name":"College Name",
                "department":"Study Program",
                "designation":"Study Program Other",
                "teaching_experience":"Semester",
                "industrial_experience":"Student Body Member",
                "highest_qualification":"Campus Ambassador History",
                "motivation":"Inspiration",
                "support_activities":"Promotion Channels",
                "student_reach":"Student Reach",
                "created_at":"Created At"
            })
        
        
        for chapter_data in serializers.data:
            activities = chapter_data['promotion_channels']
            activities_str = ", ".join(map(str, activities)) if isinstance(activities, list) else str(activities)

            lis.append({
                "name":chapter_data['full_name'],
                "email":chapter_data['email'],
                "subject":chapter_data['mobile'],
                "Chapter":chapter_data['city'],
                "Topic":chapter_data['state'],
                "total_questions":chapter_data['address'],
                "institution_name":chapter_data['college_name'],
                "department":chapter_data['program_of_study'],
                "designation":chapter_data['program_other'],
                "teaching_experience":chapter_data['semester'],
                "industrial_experience":chapter_data['student_body_member'],
                "highest_qualification":chapter_data['campus_ambassador_history'],
                "motivation":chapter_data['inspiration'],
                "support_activities":activities_str,
                "student_reach":chapter_data['student_reach'],
                "created_at":chapter_data['created_at']
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
            report_name = "student_campus_report"
            gcs_folder_name = "media/gcc_reports"
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
    ordering_fields = ["id",'first_name',"last_name","email","phone","state","city","created_at"]
    def get(self, request):
        datas = ContactUs.objects.all().order_by("-id")

        first_name = request.GET.get('first_name')
        if first_name:
            datas = datas.filter(first_name__icontains=first_name)

        last_name = request.GET.get('last_name')
        if last_name:
            datas = datas.filter(last_name__icontains=last_name)

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
        serializers = ContactListSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    

class GetContactusReportPDFView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name',"last_name","email","phone","state","city"]
    ordering_fields = ["id",'first_name',"last_name","email","phone","state","city","created_at"]
    def get(self, request):
        datas = ContactUs.objects.all().order_by("-id")

        first_name = request.GET.get('first_name')
        if first_name:
            datas = datas.filter(first_name__icontains=first_name)

        last_name = request.GET.get('last_name')
        if last_name:
            datas = datas.filter(last_name__icontains=last_name)

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

        serializers = ContactListSerializer(datas, many=True)


        data = {
                    "user_data":serializers.data,
                    "report_date": datetime.now().strftime("%d-%m-%Y, %H:%M")
                }
        

        template = get_template('pdf/contact_us_report.html')
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
            report_name = "contact_us_report"
            gcs_folder_name = "media/gcc_reports"
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
    


class GetContactusReportExcelView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name',"last_name","email","phone","state","city"]
    ordering_fields = ["id",'first_name',"last_name","email","phone","state","city","created_at"]
    def get(self, request):
        datas = ContactUs.objects.all().order_by("-id")

        first_name = request.GET.get('first_name')
        if first_name:
            datas = datas.filter(first_name__icontains=first_name)

        last_name = request.GET.get('last_name')
        if last_name:
            datas = datas.filter(last_name__icontains=last_name)

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

        serializers = ContactListSerializer(datas, many=True)

        lis = []
        
        lis.append({
                "name":"Contact Us Report",
                "last_name":'',
                "email":'',
                "subject":'',
                "Chapter":'',
                "Topic":'',
                "total_questions":''
            })

       
        lis.append({
                "name":"",
                "last_name":'',
                "email":'',
                "subject":'',
                "Chapter":'',
                "Topic":'',
                "total_questions":''
            })
        
        lis.append({
                "name":"First Name",
                "last_name":'Last Name',
                "email":'Email',
                "subject":'Phone Number',
                "Chapter":'City',
                "Topic":'State',
                "total_questions":'Created At',
            })
        
        
        for chapter_data in serializers.data:
            lis.append({
                "name":chapter_data['first_name'],
                "last_name":chapter_data['last_name'],
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
            report_name = "contact_us_report"
            gcs_folder_name = "media/gcc_reports"
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



class CreateStudentProfileView(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = CompleteStudentSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            user  = serializer.save()
            return Response({'message':'Message sent Successfully','data':[]})
        return Response(serializer.errors)


class StudentSlotBookView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request):
        datas = StudentProfile.objects.filter(user = request.user).first()
        if datas is not None:
            serializers = StudentSlotBookSerializer(datas, data=request.data, partial=True)
            if serializers.is_valid():
                serializers.save()
                return Response({"message": "Success","status":200, "data": {}})
            return Response({'message':'failed','status':400,'data':serializers.errors})

        return Response({'message':'failed','status':400, 'data':[]})
    

class StudentMockTestCompleteStatusView(APIView):
    def post(self, request):
        datas = StudentProfile.objects.filter(application_id=request.data["email"])
        if not datas:
            return Response({'message':'Invalid Account','status':400,'data':[]})
        datas = datas.first()
        serializers = StudentMockTestCompleteStatusSerializer(datas, data=request.data, partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response({"message": "Success","status":200, "data": []})
        return Response({'message':'failed','status':400, 'data':[serializers.errors]})
    

class StudentApplicationIdUpdateView(APIView):
    def post(self, request):
        usr = User.objects.all()
        for i in usr:
            StudentProfile.objects.filter(user=i).update(application_id=i.application_id)
            # print(std_profile)
        return Response({"message": "Success","status":200, "data": []})
    

class StudentMockTestStartStatusView(APIView):
    def post(self, request):
        datas = StudentProfile.objects.filter(email=request.data["email"])
        if not datas:
            return Response({'message':'Invalid Account','status':400,'data':[]})
        datas = datas.first()
        serializers = StudentMockTestStartStatusSerializer(datas, data=request.data, partial=True)
        if serializers.is_valid():
            serializers.save()
            return Response({"message": "Success","status":200, "data": []})
        return Response({'message':'failed','status':400, 'data':[serializers.errors]})
    

class GetStudentAdmitCardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        std_data = StudentProfile.objects.filter(user = request.user).first()
        static_selected_bucket = settings.GS_BUCKET_NAME
        context = {
            "username": request.user.email,
            "user_id": request.user.id,
            "application_id": request.user.application_id,
            "student_name": std_data.first_name+" "+std_data.last_name,
            "slot_date": std_data.slot_date,
            "slot_time": std_data.slot_time,
            "photo": std_data.photo.url,
            "signature": std_data.signature.url,
            "barcode":"",
            "report_date": datetime.now(),
            "test_link":"https://cocubes.in/gccschool-nfet",
            "bucket_static_logo":f"https://storage.googleapis.com/{static_selected_bucket}/static/images/gcc-admit-card-logo.jpeg",
            # "bucket_static_signature":f"https://storage.googleapis.com/{static_selected_bucket}/static/images/admit_card_signature.png"
            "bucket_static_signature":f"https://storage.googleapis.com/{static_selected_bucket}/static/images/gcc_admit_card_sign.png"
        }
        # Render template
        template = get_template("pdf/student_admit_card.html")
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
            gcs_file = f"media/admit_card/{username}_{request.user.id}.pdf"

            bucket = client.bucket(settings.GS_BUCKET_NAME_2)
            blob = bucket.blob(gcs_file)
            blob.upload_from_filename(pdf_path, content_type="application/pdf")
            # ---------- Generate signed URL ----------
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=settings.SIGNED_URL_EXPIRY),
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



class GetStudentAdmitCardAdminView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id):
        user_obj = User.objects.filter(id=id).first()
        std_data = StudentProfile.objects.filter(user = user_obj).first()
        static_selected_bucket = settings.GS_BUCKET_NAME
        context = {
            "username": user_obj.email,
            "user_id": user_obj.id,
            "application_id": user_obj.application_id,
            "student_name": std_data.first_name+" "+std_data.last_name,
            "slot_date": std_data.slot_date,
            "slot_time": std_data.slot_time,
            "photo": std_data.photo.url,
            "signature": std_data.signature.url,
            "barcode":"",
            "report_date": datetime.now(),
            "test_link":"https://cocubes.in/gccschool-nfet",
            "bucket_static_logo":f"https://storage.googleapis.com/{static_selected_bucket}/static/images/gcc-admit-card-logo.jpeg",
            # "bucket_static_signature":f"https://storage.googleapis.com/{static_selected_bucket}/static/images/admit_card_signature.png"
            "bucket_static_signature":f"https://storage.googleapis.com/{static_selected_bucket}/static/images/gcc_admit_card_sign.png"
        }
        # Render template
        template = get_template("pdf/student_admit_card.html")
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
            username = re.sub(r"\s+", "_", user_obj.email)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            gcs_file = f"media/admit_card/{username}_{user_obj.id}.pdf"

            bucket = client.bucket(settings.GS_BUCKET_NAME_2)
            blob = bucket.blob(gcs_file)
            blob.upload_from_filename(pdf_path, content_type="application/pdf")
            # ---------- Generate signed URL ----------
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=settings.SIGNED_URL_EXPIRY),
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




class GetStudentProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        datas = StudentProfile.objects.filter(user = request.user).first()
        if datas is not None:
            serializers = StudentProfileSerializer(datas)
            return Response({'message':'success',"status":200,'data':serializers.data})

        return Response({'message':'failed',"status":400,'data':[]})
    


class GetStudentReAttemptView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        status = request.data.get("status")

        if not status:
            return Response({
                "message":"Status is required",
                "status":status.HTTP_400_BAD_REQUEST,
                "data":{}
            })
        datas = StudentProfile.objects.filter(user = request.user).first()
        if datas is not None:
            serializers = StudentReAttemptSerializer(datas, data=request.data, partial=True)
            if serializers.is_valid():
                serializers.save()
                return Response({'message':'success',"status":200,'data':{}})
            else:
                return Response({'message':'failed',"status":400,'data':serializers.errors})
        return Response({'message':'failed',"status":400,'data':{}})
    


    
class GetStudentProfileListingView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name',"last_name","email","phone","state","city"]
    ordering_fields = ['first_name',"last_name","email","phone","state","city","created_at","slot_date"]
    def get(self, request):
        datas = StudentProfile.objects.all().order_by('-id')

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
        
        # slot_date range filter
        start_slot_date = request.GET.get('start_slot_date')
        end_slot_date = request.GET.get('end_slot_date')
        if start_slot_date:
            datas = datas.filter(slot_date__gte=start_slot_date)

        if end_slot_date:
            datas = datas.filter(slot_date__lte=end_slot_date)


        search_filter = filters.SearchFilter()
        datas = search_filter.filter_queryset(request, datas, self)

        ordering_filter = filters.OrderingFilter()
        datas = ordering_filter.filter_queryset(request, datas, self)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(datas, request, view=self)
        serializers = StudentProfileSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    




class GetStudentScoreCardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_obj = request.user

        std_data = StudentProfile.objects.filter(user=user_obj).first()
        score_objs = StudentExamResult.objects.filter(student_profile=std_data).first()

        if not score_objs:
            return Response({"message": "No data found"},data={}, status=404)
        
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
            "application_id":user_obj.application_id,
            "date_of_exam":std_data.slot_date,
            "time_of_exam":std_data.slot_time,
            "sections":datas,
            "total_questions":score_objs.totalquestions,
            "total_correct":score_objs.totalcorrectanswers,
            "total_incorrect":int(float(score_objs.totalquestionsattempted) - float(score_objs.totalcorrectanswers)),
            "total_not_attempted":int(float(score_objs.totalquestions) - float(score_objs.totalquestionsattempted)),

            "username": user_obj.email,
            "user_id": user_obj.id,
            "application_id": user_obj.application_id,
            "student_name": f'''{std_data.first_name.upper()}" "{std_data.last_name.upper()}''',
            "slot_date": std_data.slot_date,
            "slot_time": std_data.slot_time,
            "photo": std_data.photo.url,
            "signature": std_data.signature.url,
            "barcode":"",
            "report_date": datetime.now(),
            "test_link":"https://cocubes.in/gccschool-nfet",
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
            return Response({"error": "PDF generation failed"}, status=500)
        try:
            # Upload to GCS
            username = re.sub(r"\s+", "_", user_obj.email)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            gcs_file = f"media/admit_card/{username}_{user_obj.id}.pdf"

            bucket = client.bucket(settings.GS_BUCKET_NAME_2)
            blob = bucket.blob(gcs_file)
            blob.upload_from_filename(pdf_path, content_type="application/pdf")
            # ---------- Generate signed URL ----------
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=settings.SIGNED_URL_EXPIRY),
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


class GetAdminStudentScoreCardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, stid):
        
        std_data = StudentProfile.objects.filter(id=stid).first()
        score_objs = StudentExamResult.objects.filter(student_profile=std_data).first()

        if not score_objs:
            return Response({"message": "No data found"},data={}, status=404)
        
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
            "test_link":"https://cocubes.in/gccschool-nfet",
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
            return Response({"error": "PDF generation failed"}, status=500)
        try:
            # Upload to GCS
            username = re.sub(r"\s+", "_", std_data.email)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            gcs_file = f"media/admit_card/{username}_{std_data.id}.pdf"

            bucket = client.bucket(settings.GS_BUCKET_NAME_2)
            blob = bucket.blob(gcs_file)
            blob.upload_from_filename(pdf_path, content_type="application/pdf")
            # ---------- Generate signed URL ----------
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=settings.SIGNED_URL_EXPIRY),
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



#########################################################################################


class StudentCreatePaymentView(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        serializers = StudentCreatePaymentSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response({'message':'success',"status":200,'data':{}})
        else:
            return Response({'message':'failed',"status":400,'data':serializers.errors})
    


class PostExamResultView(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        print(request.data)
        serializers = PostExamResultSerializer(data=request.data)
        if serializers.is_valid():
            datas = serializers.save()
            print(datas)
            print(type(datas))
            print(datas.json_data)
            datas.json_data = request.data["competency"]
            datas.save()
            return Response({'message':'success',"status":200,'data':{}})
        else:
            return Response({'message':'failed',"status":400,'data':serializers.errors})
    




