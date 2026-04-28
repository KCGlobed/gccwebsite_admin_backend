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


from .serializers import push_to_meritto
class DossierMeritto_CreateUpdate(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        data_list = []
        dossier_obj = DossierData.objects.filter(id=4561)
        filter_data = dossier_obj.count()
        for obj in dossier_obj:
            push_to_meritto(obj)
            # serializer = CreateOrUpdateDossierDataMerittoSerializer(obj, data = request.data)
            # if serializer.is_valid(raise_exception = True):
            #     serializer.save()
            data_list.append(obj.id)
        total_lead = len(data_list)
        return success_response(message="success", data={"total_lead":total_lead,"filter_data":filter_data,"ids":data_list}, status_code=status.HTTP_200_OK)


class DossierDocument_Create(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = CreateDossierDocumentSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            obj = serializer.save()
            return success_response(message="success", data={"id":obj.id}, status_code=status.HTTP_200_OK)
        else:
            return error_response(message="failed", data = {}, status_code=status.HTTP_400_BAD_REQUEST)


class DossierAbondant_Create(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = CreateDossierAbondantSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            obj = serializer.save()
            return success_response(message="success", data={"id":obj.id}, status_code=status.HTTP_200_OK)
        else:
            return error_response(message="failed", data = {}, status_code=status.HTTP_400_BAD_REQUEST)


class VslDataForm_Create(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = CreateVslDataSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            obj = serializer.save()
            return success_response(message="success", data={"id":obj.id, "data":ListDossierDataSerializer(obj).data}, status_code=status.HTTP_200_OK)
        else:
            return error_response(message="failed", data = {}, status_code=status.HTTP_400_BAD_REQUEST)


class VslFinalDataForm_Create(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = CreateVslFinalDataSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            obj = serializer.save()
            return success_response(message="success", data={"id":obj.id, "data":ListDossierDataSerializer(obj).data}, status_code=status.HTTP_200_OK)
        else:
            return error_response(message="failed", data = {}, status_code=status.HTTP_400_BAD_REQUEST)


class VslOptinDetailDataForm_Create(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = CreateVslOptinDetailDataSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            obj = serializer.save()
            return success_response(message="success", data={}, status_code=status.HTTP_200_OK)
        else:
            return error_response(message="failed", data = {}, status_code=status.HTTP_400_BAD_REQUEST)


class VslOptinDetailDataForm_Update(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = UpdateVslOptinDetailDataSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            obj = serializer.save()
            return success_response(message="success", data={}, status_code=status.HTTP_200_OK)
        else:
            return error_response(message="failed", data = {}, status_code=status.HTTP_400_BAD_REQUEST)



class DossierDataForm_List(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"full_name","email","phone","city","state"]
    ordering_fields = ['id',"full_name","email","phone","city","state","created_at"]
    def get(self, request):

        document_status = request.GET.get('document_status')
        if document_status:
            datas = DossierData.objects.filter(
                    source=SourceType.Website
                ).annotate(
                    has_doc=Exists(
                        DossierDocument.objects.filter(dossier_id=OuterRef('id'))
                    )
                ).filter(has_doc=True).order_by('-id')
        else:
            datas = DossierData.objects.filter(source=SourceType.Website).order_by('-id')
        
        verify_status = request.GET.get('isVerified')
        if verify_status:
            if str(verify_status) in ["2","3"]:
                datas = datas.filter(document_status=int(verify_status))
                
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
    

class AbondantDataForm_List(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"full_name","email","phone"]
    ordering_fields = ['id',"full_name","email","phone","created_at"]
    def get(self, request):
        source = request.GET.get('source')
        if source:
            datas = DossierAbondant.objects.filter(source=source).order_by('-id')
        else:
            datas = DossierAbondant.objects.all().order_by('-id')

        full_name = request.GET.get('full_name')
        if full_name:
            datas = datas.filter(full_name__icontains=full_name)

        email = request.GET.get('email')
        if email:
            datas = datas.filter(email__icontains=email)


        phone = request.GET.get('phone')
        if phone:
            datas = datas.filter(phone__icontains=phone)


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
        serializers = ListDossierAbondantSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)
    

class DossierDataSourceForm_List(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"full_name","email","phone","city","state"]
    ordering_fields = ['id',"full_name","email","phone","city","state","created_at"]
    def get(self, request):

        source_type = request.GET.get('source')
        if source_type:
            # datas = DossierData.objects.filter(source=source_type).order_by('-id')
            document_status = request.GET.get('document_status')
            if document_status:
                datas = DossierData.objects.filter(
                        source=source_type
                    ).annotate(
                        has_doc=Exists(
                            DossierDocument.objects.filter(dossier_id=OuterRef('id'))
                        )
                    ).filter(has_doc=True).order_by('-id')
            else:
                datas = DossierData.objects.filter(source=source_type).order_by('-id')
        else:
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
        document_status = request.GET.get('document_status')
        if document_status:
            datas = DossierData.objects.filter(
                    source=SourceType.Website
                ).annotate(
                    has_doc=Exists(
                        DossierDocument.objects.filter(dossier_id=OuterRef('id'))
                    )
                ).filter(has_doc=True).order_by('-id')
        else:
            datas = DossierData.objects.filter(source=SourceType.Website).order_by('-id')
        
        verify_status = request.GET.get('isVerified')
        if verify_status:
            if str(verify_status) in ["2","3"]:
                datas = datas.filter(document_status=int(verify_status))
                
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



        # datas = DossierData.objects.filter(source=SourceType.Website).order_by('-id')

        # full_name = request.GET.get('full_name')
        # if full_name:
        #     datas = datas.filter(full_name__icontains=full_name)

        # email = request.GET.get('email')
        # if email:
        #     datas = datas.filter(email__icontains=email)


        # phone = request.GET.get('phone')
        # if phone:
        #     datas = datas.filter(phone__icontains=phone)


        # state = request.GET.get('state')
        # if state:
        #     datas = datas.filter(state__icontains=state)

        # city = request.GET.get('city')
        # if city:
        #     datas = datas.filter(city__icontains=city)

        # # Date range filter
        # start_date = request.GET.get('start_date')
        # end_date = request.GET.get('end_date')
        # if start_date:
        #     start_date = parse_date(start_date)
        #     if start_date:
        #         datas = datas.filter(created_at__date__gte=start_date)

        # if end_date:
        #     end_date = parse_date(end_date)
        #     if end_date:
        #         datas = datas.filter(created_at__date__lte=end_date)


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
            gcs_folder_name = "media/reports/dossier/pdf"
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
                "fbc_id":'',
                "utm_source":'',
                "utm_medium":'',
                "utm_content":'',
                "utm_campaign":'',
                "campaign_id":'',
                "utm_adname":'',
                "adset_id":'',
                "fbclid":'',
                "ad_source":'',
                "ad_id":'',
                "university":'',
                "remarks":'',
                "remarks_timestamp":'',
                "fee_waiver_category":'',
                "total_questions":''
            })

       
        lis.append({
                "name":"",
                "email":'',
                "subject":'',
                "Chapter":'',
                "Topic":'',
                "fbc_id":'',
                "utm_source":'',
                "utm_medium":'',
                "utm_content":'',
                "utm_campaign":'',
                "campaign_id":'',
                "utm_adname":'',
                "adset_id":'',
                "fbclid":'',
                "ad_source":'',
                "ad_id":'',
                "university":'',
                "remarks":'',
                "remarks_timestamp":'',
                "fee_waiver_category":'',
                "total_questions":''
            })
        
        lis.append({
                "name":"Full Name",
                "email":'Email',
                "subject":'Phone Number',
                "Chapter":'City',
                "Topic":'State',
                "fbc_id":'Fbc Id',
                "utm_source":'UTM Source',
                "utm_medium":'UTM Medium',
                "utm_content":'UTM Content',
                "utm_campaign":'UTM Campaign',
                "campaign_id":'Campaign Id',
                "utm_adname":'UTM Adname',
                "adset_id":'Adset Id',
                "fbclid":'Fbclid',
                "ad_source":'Ad Source',
                "ad_id":'Ad Id',
                "university":'University',
                "remarks":'Remarks',
                "remarks_timestamp":'Remarks Timestamp',
                "fee_waiver_category":'Fee Waiver Category',
                "total_questions":'Created At'
            })
        
        
        for chapter_data in serializers.data:
            lis.append({
                "name":chapter_data['full_name'],
                "email":chapter_data['email'],
                "subject":chapter_data['phone'],
                "Chapter":chapter_data['city'],
                "Topic":chapter_data['state'],
                "fbc_id":chapter_data['fbc_id'],
                "utm_source":chapter_data['utm_source'],
                "utm_medium":chapter_data['utm_medium'],
                "utm_content":chapter_data['utm_content'],
                "utm_campaign":chapter_data['utm_campaign'],
                "campaign_id":chapter_data['campaign_id'],
                "utm_adname":chapter_data['utm_adname'],
                "adset_id":chapter_data['adset_id'],
                "fbclid":chapter_data['fbclid'],
                "ad_source":chapter_data['ad_source'],
                "ad_id":chapter_data['ad_id'],
                "university":chapter_data['university'],
                "remarks":chapter_data['remarks'],
                "remarks_timestamp":chapter_data['remarks_timestamp'],
                "fee_waiver_category":chapter_data['fee_waiver_category'],
                "total_questions":chapter_data['created_at']
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
            gcs_folder_name = "media/reports/dossier/excel"
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




############################ For Affiliates ##########################



class GetDossierSourceReportPDFView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"full_name","email","phone","city","state"]
    ordering_fields = ['id',"full_name","email","phone","city","state","created_at"]
    def get(self, request, sid=None):
        source_type = request.GET.get('source')
        if source_type:
            datas = DossierData.objects.filter(source=source_type).order_by('-id')
        else:
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
            gcs_folder_name = "media/source/excel"
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
    

class GetDossierVSLSourceReportPDFView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"full_name","email","degree","degree_stage","phone"]
    ordering_fields = ['id',"full_name","email","phone","degree","degree_stage","created_at"]
    def get(self, request, sid=None):
        source_type = request.GET.get('source')
        if source_type:
            datas = DossierData.objects.filter(source=source_type).order_by('-id')
        else:
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

        degree = request.GET.get('degree')
        if degree:
            datas = datas.filter(degree__icontains=degree)

        degree_stage = request.GET.get('degree_stage')
        if degree_stage:
            datas = datas.filter(degree_stage__icontains=degree_stage)

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
        

        template = get_template('pdf/vsl_report.html')
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
            report_name = "vsl_report"
            gcs_folder_name = "media/reports/vsl/pdf"
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
    


class GetDossierSourceReportExcelView(APIView):
    # permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"full_name","email","phone","city","state"]
    ordering_fields = ['id',"full_name","email","phone","city","state","created_at"]

    def get(self, request, sid=None):
        
        source_type = request.GET.get('source')
        if source_type:
            datas = DossierData.objects.filter(source=source_type).order_by('-id')
        else:
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
                "fbc_id":'',
                "utm_source":'',
                "utm_medium":'',
                "utm_content":'',
                "utm_campaign":'',
                "campaign_id":'',
                "utm_adname":'',
                "adset_id":'',
                "fbclid":'',
                "ad_source":'',
                "ad_id":'',
                "university":'',
                "remarks":'',
                "remarks_timestamp":'',
                "fee_waiver_category":'',
                "total_questions":''
            })

       
        lis.append({
                "name":"",
                "email":'',
                "subject":'',
                "Chapter":'',
                "Topic":'',
                "fbc_id":'',
                "utm_source":'',
                "utm_medium":'',
                "utm_content":'',
                "utm_campaign":'',
                "campaign_id":'',
                "utm_adname":'',
                "adset_id":'',
                "fbclid":'',
                "ad_source":'',
                "ad_id":'',
                "university":'',
                "remarks":'',
                "remarks_timestamp":'',
                "fee_waiver_category":'',
                "total_questions":''
            })
        
        lis.append({
                "name":"Full Name",
                "email":'Email',
                "subject":'Phone Number',
                "Chapter":'City',
                "Topic":'State',
                "fbc_id":'Fbc Id',
                "utm_source":'UTM Source',
                "utm_medium":'UTM Medium',
                "utm_content":'UTM Content',
                "utm_campaign":'UTM Campaign',
                "campaign_id":'Campaign Id',
                "utm_adname":'UTM Adname',
                "adset_id":'Adset Id',
                "fbclid":'Fbclid',
                "ad_source":'Ad Source',
                "ad_id":'Ad Id',
                "university":'University',
                "remarks":'Remarks',
                "remarks_timestamp":'Remarks Timestamp',
                "fee_waiver_category":'Fee Waiver Category',
                "total_questions":'Created At'
            })
        
        
        for chapter_data in serializers.data:
            lis.append({
                "name":chapter_data['full_name'],
                "email":chapter_data['email'],
                "subject":chapter_data['phone'],
                "Chapter":chapter_data['city'],
                "Topic":chapter_data['state'],
                "fbc_id":chapter_data['fbc_id'],
                "utm_source":chapter_data['utm_source'],
                "utm_medium":chapter_data['utm_medium'],
                "utm_content":chapter_data['utm_content'],
                "utm_campaign":chapter_data['utm_campaign'],
                "campaign_id":chapter_data['campaign_id'],
                "utm_adname":chapter_data['utm_adname'],
                "adset_id":chapter_data['adset_id'],
                "fbclid":chapter_data['fbclid'],
                "ad_source":chapter_data['ad_source'],
                "ad_id":chapter_data['ad_id'],
                "university":chapter_data['university'],
                "remarks":chapter_data['remarks'],
                "remarks_timestamp":chapter_data['remarks_timestamp'],
                "fee_waiver_category":chapter_data['fee_waiver_category'],
                "total_questions":chapter_data['created_at']
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
            gcs_folder_name = "media/reports/source/excel"
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

class GetAmendmentSourceReportExcelView(APIView):
    # permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"full_name","email","phone"]
    ordering_fields = ['id',"full_name","email","phone","created_at"]

    def get(self, request, sid=None):
        
        source_type = request.GET.get('source')
        if source_type:
            datas = DossierAbondant.objects.filter(source=source_type).order_by('-id')
        else:
            datas = DossierAbondant.objects.filter(source=SourceType.Website).order_by('-id')

        full_name = request.GET.get('full_name')
        if full_name:
            datas = datas.filter(full_name__icontains=full_name)

        email = request.GET.get('email')
        if email:
            datas = datas.filter(email__icontains=email)


        phone = request.GET.get('phone')
        if phone:
            datas = datas.filter(phone__icontains=phone)

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

        serializers = ListDossierAbondantSerializer(datas, many=True)

        lis = []
        
        lis.append({
                "full_name":"Amendment Report",
                "email":'',
                "phone":'',
                "utm_source":'',
                "utm_medium":'',
                "utm_campaign":'',
                "created_at":''
            })

       
        lis.append({
                "full_name":"",
                "email":'',
                "phone":'',
                "utm_source":'',
                "utm_medium":'',
                "utm_campaign":'',
                "created_at":''
            })
        
        lis.append({
                "full_name":"Full Name",
                "email":'Email',
                "phone":'Phone Number',
                "utm_source":'UTM Source',
                "utm_medium":'UTM Medium',
                "utm_campaign":'UTM Campaign',
                "created_at":'Date Time'
            })
        
        
        for chapter_data in serializers.data:
            lis.append({
                "full_name":chapter_data["full_name"],
                "email":chapter_data["email"],
                "phone":chapter_data["phone"],
                "utm_source":chapter_data["utm_source"],
                "utm_medium":chapter_data["utm_medium"],
                "utm_campaign":chapter_data["utm_campaign"],
                "created_at":chapter_data["created_at"]
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
            report_name = "amendment_report"
            gcs_folder_name = "media/reports/source/excel"
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



class GetDossierVSLSourceReportExcelView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"full_name","email","phone","city","state"]
    ordering_fields = ['id',"full_name","email","phone","city","state","created_at"]

    def get(self, request, sid=None):
        
        source_type = request.GET.get('source')
        if source_type:
            datas = DossierData.objects.filter(source=source_type).order_by('-id')
        else:
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


        degree = request.GET.get('degree')
        if degree:
            datas = datas.filter(degree__icontains=degree)

        degree_stage = request.GET.get('degree_stage')
        if degree_stage:
            datas = datas.filter(degree_stage__icontains=degree_stage)

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
                "name":"VSL Report",
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
                "Chapter":'Degree',
                "Topic":'Degree Stage',
                "total_questions":'Created At',
            })
        
        
        for chapter_data in serializers.data:
            lis.append({
                "name":chapter_data['full_name'],
                "email":chapter_data['email'],
                "subject":chapter_data['phone'],
                "Chapter":chapter_data['degree'],
                "Topic":chapter_data['degree_stage'],
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
            report_name = "vsl_report"
            gcs_folder_name = "media/reports/vsl/excel"
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





class GetDeleteLead(APIView):
    def get(self, request, sid=None):
        print("deleting.....")
        # d_list = [257,694,727,744,748,750,752,773,774,782,894,254,503,1147,3561,3795,3524,3780,3526,4109,1171,1270,4109]
        # d_list = [284]
        d_list = []
        for i in d_list:
            d = DossierData.objects.filter(id=i)
            if d:
                d.first().delete()
                print(i,">>>>>>deleted....")
        return success_response(
                message="Success",
                data={},
                status_code=status.HTTP_200_OK
            )