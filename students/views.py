from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework import filters
from gcc_backend.pagination import CustomPageNumberPagination
from rest_framework.permissions import IsAuthenticated


# Create your views here.

class StudentQuery_list(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id']
    ordering_fields = ['id']
    def get(self, request):
        datas = StudentEnquiries.objects.all().order_by('-id')
        dd = StudentDocuments.objects.all()
        ddd = StudentsData.objects.all()
        dddd = Payments.objects.all()
        print("dd",dd)
        print("ddd",ddd)
        print("dddd",dddd)
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
        dd = StudentDocuments.objects.all()
        ddd = StudentsData.objects.all()
        dddd = Payments.objects.all()
        print("dd",dd)
        print("ddd",ddd)
        print("dddd",dddd)
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
        print(serializers)
        
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
        print(serializers)
        
        return paginator.get_paginated_response(serializers.data)
    
from django.conf import settings
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import get_template
from google.cloud import storage
# client = storage.Client()
import os
client = storage.Client.from_service_account_json(os.path.join(settings.BASE_DIR, 'credentail_bucket.json'))
import pandas as pd
import tempfile
import re
from datetime import datetime, timedelta

# from django.core.files.storage import default_storage
# from django.core.files.base import ContentFile
# print([b.name for b in client.list_buckets()])




# class GetSessionReportPDFView(APIView):
#     # renderer_classes = [ReportsRenderer]
#     permission_classes = [IsAuthenticated]
#     # @auto_logout
#     def get(self, request):
#         print("system default...:", settings.GS_BUCKET_NAME)
#         bucket = client.get_bucket(settings.GS_BUCKET_NAME)
#         print(bucket.name)
#         return Response({"status":"success"})
    




def web(request):
    data_objs = CampusStudent.objects.all().order_by("-id")
    data_list = ListCampusStudentSerializer(data_objs, many=True).data

    # Flatten serializer data (IMPORTANT for xhtml2pdf)
    clean_list = []
    for row in data_list:
        clean_list.append({
            "full_name": row.get("full_name", ""),
            "email": row.get("email", ""),
            "mobile": row.get("mobile", ""),
            "city": row.get("city", ""),
            "state": row.get("state", ""),
            "address": row.get("address", ""),
            "college_name": row.get("college_name", ""),
            "program_of_study": row.get("program_of_study", ""),
            "program_other": row.get("program_other", ""),
            "semester": row.get("semester", ""),
            "student_body_member": row.get("student_body_member", ""),
            "campus_ambassador_history": row.get("campus_ambassador_history", ""),
            "inspiration": row.get("inspiration", ""),
            "student_reach": row.get("student_reach", ""),
            "consent": row.get("consent", "")
        })
    context = {
        "username": request.user.email,
        "user_id": request.user.id,
        "data_list": clean_list,
        "report_date": datetime.now()
    }
    return render(request, 'pdf/session_report.html', context)




class GetSessionReportPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        data_objs = CampusStudent.objects.all().order_by("-id")
        data_list = CampusStudentPDFSerializer(data_objs, many=True).data

        # # Flatten serializer data (IMPORTANT for xhtml2pdf)
        # clean_list = []
        # for row in data_list:
        #     clean_list.append({
        #         "full_name": row.get("full_name", ""),
        #         "email": row.get("email", ""),
        #         "mobile": row.get("mobile", ""),
        #         "city": row.get("city", ""),
        #         "state": row.get("state", ""),
        #         "address": row.get("address", ""),
        #         "college_name": row.get("college_name", ""),
        #         "program_of_study": row.get("program_of_study", ""),
        #         "program_other": row.get("program_other", ""),
        #         "semester": row.get("semester", ""),
        #         "student_body_member": row.get("student_body_member", ""),
        #         "campus_ambassador_history": row.get("campus_ambassador_history", ""),
        #         "inspiration": row.get("inspiration", ""),
        #         "student_reach": row.get("student_reach", ""),
        #         "consent": row.get("consent", "")
        #     })
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




# from weasyprint import HTML

# class GetSessionReportPDFView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):

#         data = {}
#         data_objs = CampusStudent.objects.all().order_by('-id')
#         data_list = ListCampusStudentSerializer(data_objs, many=True).data
#         data["username"] = request.user.email
#         data["user_id"] = request.user.id
#         data["data_list"] = data_list
#         data["report_date"] = "30-01-2026"
#         print(data)
#         template = get_template('pdf/session_report.html')
#         html = template.render(data)

#         # ---------- Create temp PDF ----------
#         with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
#             pdf_path = temp_file.name
#             html = html.encode("latin-1", "replace").decode("latin-1")
#             pisa.CreatePDF(BytesIO(html.encode("ISO-8859-1")), dest=temp_file)
            
#             # HTML(string=html).write_pdf(pdf_path)
#         try:
#             # ---------- GCS Path ----------
#             username = re.sub(r"\s+", "_", data["username"])
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             gcs_file_name = f"media/kcc_data_list/reports/{username}_session_report_{timestamp}.pdf"

#             # ---------- Upload to GCS ----------
#             bucket = client.bucket(settings.GS_BUCKET_NAME)
#             blob = bucket.blob(gcs_file_name)
#             blob.upload_from_filename(pdf_path, content_type="application/pdf")

#             # ---------- Generate signed URL ----------
#             url = blob.generate_signed_url(
#                 version="v4",
#                 expiration=timedelta(minutes=30),
#                 method="GET"
#             )

#             return Response({
#                 "message": "Success",
#                 "data": {
#                     "report_url": url
#                 },
#                 "status": 200
#             })

#         finally:
#             os.remove(pdf_path)


# class GetSessionReportPDFView(APIView):
#     # renderer_classes = [ReportsRenderer]
#     permission_classes = [IsAuthenticated]
#     # @auto_logout
#     def get(self, request, sid=None):
        
#         datas = CampusStudent.objects.all().order_by('-id')
#         completed_session = ListCampusStudentSerializer(datas, context={'user':request.user,"subject_id":sid,"session_type":"completed"})


#         data = {
#                     'username':request.user.first_name +' '+request.user.last_name,
#                     'user_id':request.user.email
#                 }
        

#         template = get_template('pdf/session_report.html')
#         html  = template.render(data)
#         with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
#             pdf_path = temp_file.name
            
#             # Encode HTML and create PDF
#             html = html.encode('latin-1', 'replace').decode('latin-1')
#             pdf = pisa.CreatePDF(BytesIO(html.encode("ISO-8859-1")), dest=temp_file)

#             if pdf.err:
#                 raise Exception("PDF generation error!")
        
#         # After the 'with' block, the file is closed, but not deleted yet
#         try:
#             # GCS file naming logic
#             timestamp = datetime.now().strftime("%d_%m_%y_%H_%M")
#             report_name = "session_report"
#             username = re.sub(r'\s+', '_', f"{request.user.first_name} {request.user.last_name}")
#             gcs_folder_name = "media/kcc_data_list/reports"
#             # gcs_file_name = f"{gcs_folder_name}/{username}_{report_name}_{timestamp}.pdf"
#             gcs_file_name = f"{gcs_folder_name}/{username}_{report_name}.pdf"

#             # Upload the temporary file to GCS
#             bucket = client.get_bucket(settings.GS_BUCKET_NAME)
#             # bucket = client.get_bucket("kcc_report_data")
#             print("bcket...",bucket)
#             blob = bucket.blob(gcs_file_name)
#             blob.upload_from_filename(pdf_path)
#             url = blob.generate_signed_url(
#                 version="v4",
#                 expiration=timedelta(minutes=30),   # link valid for 30 minutes
#                 method="GET"
#             )
#             return Response({
#                 "message":"Success",
#                 "data":{"report_url": url},
#                 "status":200}
#             )
#         finally:
#             print("calleddd...")
#             # Ensure the temporary file is deleted from the server's disk
#             os.remove(pdf_path)





# from google.cloud import storage
# from datetime import datetime, timedelta
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from django.template.loader import get_template
# from io import BytesIO
# from xhtml2pdf import pisa
# import tempfile, os, re


# class GetSessionReportPDFView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, sid=None):

#         data = {
#             'username': f"{request.user.first_name} {request.user.last_name}",
#             'user_id': request.user.email
#         }

#         # Render HTML
#         template = get_template('pdf/session_report.html')
#         html = template.render(data)

#         # Create PDF
#         with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
#             pdf_path = temp_file.name
#             pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=temp_file)

#         try:
#             # GCS file naming
#             timestamp = datetime.now().strftime("%d_%m_%y_%H_%M")
#             username = re.sub(r'\s+', '_', data["username"])
#             gcs_file_name = (
#                 f"media/kcc_data_list/reports/"
#                 f"{username}_session_report_{timestamp}.pdf"
#             )

#             # Upload to GCS
#             client = storage.Client()
#             bucket = client.bucket("kcc_report_data")
#             blob = bucket.blob(gcs_file_name)
#             blob.upload_from_filename(
#                 pdf_path,
#                 content_type="application/pdf"
#             )

#             # ✅ Generate SIGNED URL (THIS IS THE KEY)
#             signed_url = blob.generate_signed_url(
#                 version="v4",
#                 expiration=timedelta(minutes=15),
#                 method="GET"
#             )

#             return Response({
#                 "message": "Success",
#                 "data": {
#                     "report_url": signed_url
#                 }
#             }, status=200)

#         finally:
#             os.remove(pdf_path)
