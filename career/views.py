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
            source = request.data.get("source")
            if str(source)=="16":
                pdf_url = f"{settings.STATIC_URL}files/CPA-STUDENT-DOSSIER.pdf"
            elif str(source)=="17":
                pdf_url = f"{settings.STATIC_URL}files/EA-STUDENT-DOSSIER.pdf"
            else:
                pdf_url = f"{settings.STATIC_URL}files/GCC%20SCHOOL%20Dossier.pdf"
            return success_response(message="success", data={"url":pdf_url, "id":obj.id, "data":ListDossierDataSerializer(obj).data}, status_code=status.HTTP_200_OK)
        else:
            return error_response(message="failed", data = {}, status_code=status.HTTP_400_BAD_REQUEST)


class DossierDataFormCustom_Create(APIView):
    def post(self, request, format=None):
        serializer = CreateDossierDataCustomAffliateSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            obj = serializer.save()
            start_date = date(2026, 6, 22)
            end_date = date(2026, 7, 13)
            # Count records grouped by interview_date
            booked_slots = (
                ManageStudentInterview.objects
                .filter(interview_date__range=(start_date, end_date))
                .annotate(day=TruncDate("interview_date"))
                .values("day")
                .annotate(count=Count("id"))
                .order_by("day")
            )
            # Convert queryset to dictionary
            count_map = {item["day"]: item["count"] for item in booked_slots}  

            # Fill missing dates with 0
            result = []
            current = start_date

            while current <= end_date:
                result.append({
                    "date": current.strftime("%d-%m-%Y"),
                    "count": count_map.get(current, 0)
                })
                current += timedelta(days=1)

            return success_response(message="success", data={"id":obj.id, "slot_data":result}, status_code=status.HTTP_200_OK)
        else:
            return error_response(message="failed", data = [], status_code=status.HTTP_400_BAD_REQUEST)





class InterviewSlotScheduleAdmin_list(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["full_name","email", "phone", "interview_date"]
    ordering_fields = ["id"]
    def get(self, request):
        datas = DossierData.objects.filter(source=SourceType.Affiliate7).order_by('-id')

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
        serializers = ListDossierDataAffliateSevenInterviewSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializers.data)






from .serializers import push_to_meritto
class DossierMeritto_CreateUpdate(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        data_list = []
        j = 0
        # yesterday = datetime.now().date() - timedelta(days=2)
        today = datetime.now().date()
        # dossier_obj = DossierData.objects.filter(created_at__date__gte='2026-05-15', source=SourceType.Website)
        # dossier_obj = dossier_obj.filter(created_at__date__lte='2026-05-18')
        dossier_obj = DossierData.objects.filter(id=request.data['lid'])
        filter_data = dossier_obj.count()
        print("count data...",filter_data)
        cc = filter_data
        # objj = list(User.objects.values_list('email', flat=True))

        # print(objj)
        # print(len(objj))
        
        
        for obj in dossier_obj:
            # if obj.email in objj:
            #     print("email.......",obj.email)
            #     push_to_meritto(obj)


            # serializer = CreateOrUpdateDossierDataMerittoSerializer(obj, data = request.data)
            # if serializer.is_valid(raise_exception = True):
            #     serializer.save()


                # data_list.append(obj.id)
                
            push_to_meritto(obj)
            data_list.append(obj.id)
            # break
            j+=1
            cc-=1
            print("++++++",j)
            print("------",cc)
        total_lead = len(data_list)

        return success_response(message="success", data={"total_lead":total_lead,"filter_data":filter_data,"ids":data_list}, status_code=status.HTTP_200_OK)




class ExcelPhoneMatchAPI(APIView):

    def post(self, request, *args, **kwargs):
        print("calling...!!")
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read Excel file
            df = pd.read_excel(file)

            # Ensure column exists (change 'phone' to your column name)
            if 'Mobile' not in df.columns:
                return Response({"error": "Column 'mobile' not found in file"}, status=400)

            # Clean phone numbers
            df['Mobile'] = df['Mobile'].astype(str).str.strip()

            phone_list = df['Mobile'].dropna().unique().tolist()
            data_list = []
            j = 0
            print("listing data.....",phone_list)
            for i in phone_list:
                print(i[4:])
                matched_data = DossierData.objects.filter(phone=i[5:], source=12).first()
                print(matched_data)
                if matched_data:
                    push_to_meritto(matched_data)
                    data_list.append(matched_data.id)
                    # break
                    print("success")
                j+=1
                print(j)
            total_lead = len(data_list)
            

            # # Query DB
            # matched_data = DossierData.objects.filter(
            #     phone__in=phone_list
            # ).values('id', 'email', 'phone', 'created_at')

            # matched_phones = {item['phone'] for item in matched_data}

            # # Logic: find unmatched numbers
            # unmatched = [p for p in phone_list if p not in matched_phones]


            # url = f"{settings.MERITO_BASE_URL}/lead/v1/createOrUpdate"

            # headers = {
            #     "Content-Type": "application/json",
            #     "secret-key": settings.MERITO_SECRETE_KEY,
            #     "access-key": settings.MERITO_ACCESS_KEY
            # }

            # payload = {
            #     "name": obj.full_name,
            #     "email": obj.email,
            #     "mobile": obj.phone,
            #     "search_criteria": "mobile",
            #     "country": "India",
            #     "source": "gccvsloptin",
            #     "cf_source": "gccvsloptin",
            #     "cf_utmsource1": str(obj.utm_source).encode("ascii", "ignore").decode().strip(),
            #     "medium": str(obj.utm_medium).encode("ascii", "ignore").decode().strip(),
            #     "campaign": str(obj.utm_campaign).encode("ascii", "ignore").decode().strip(),
            #     # "cf_payment_status": "Complete",
            # }
            # if obj.city:
            #     payload["city"] = obj.city
            # if obj.state:
            #     payload["state"] = obj.state
            # if obj.university:
            #     payload["cf_fee_waiver_category"] = obj.fee_waiver_category

            # print("merito data.......",payload)

            # try:
            #     response = requests.post(url, headers=headers, json=payload)
            #     print(response.status_code)
            #     print(response.text)
            #     return response.json()
            # except requests.exceptions.RequestException as e:
            #     print("Meritto API Error:", str(e))
            #     return None





            return Response({
                "total_uploaded": len(phone_list),
                "total_lead": total_lead,
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)







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
    search_fields = ['id',"full_name","email","phone","city","state","referred_code","referral_code"]
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

        fee_waiver_category = request.GET.get('fee_waiver_category')
        if fee_waiver_category:
            datas = datas.filter(fee_waiver_category__icontains=fee_waiver_category)

        university = request.GET.get('university')
        if university:
            datas = datas.filter(university__icontains=university)

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
    search_fields = ['id',"full_name","email","phone","city","state","referred_code","referral_code"]
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
    

class VSLAdvisorDataForm_List(APIView):
    # permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"full_name","email","phone","city","state"]
    ordering_fields = ['id',"full_name","email","phone","city","state","created_at"]
    def get(self, request):
        
        adv_datas_list = list(VslDetail.objects.filter(specialist_status=True).values_list('dossier__id',flat=True))
        # print(adv_datas_list)
        datas = DossierData.objects.filter(id__in=adv_datas_list, source=SourceType.VslOptin).order_by('-id')


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
                "total_questions":'',
                "document_status":'',
                "referral_code":'',
                "referred_code":'',
                "program":'',
                "reffered_by":''
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
                "total_questions":'',
                "document_status":'',
                "referral_code":'',
                "referred_code":'',
                "program":'',
                "reffered_by":''
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
                "total_questions":'Created At',
                "document_status":'Document Status',
                "referral_code":'Referral Code',
                "referred_code":'Referred Code',
                "program":'Program',
                "reffered_by":'Reffered By'
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
                "total_questions":chapter_data['created_at'],
                "document_status":chapter_data['document_status'],
                "referral_code":chapter_data['referral_code'],
                "referred_code":chapter_data['referred_code'],
                "program":chapter_data['program'],
                "reffered_by":chapter_data['reffered_by']
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
    




class GetVSLAdvisorReportPDFView(APIView):
    # permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"full_name","email","phone","city","state"]
    ordering_fields = ['id',"full_name","email","phone","city","state","created_at"]
    def get(self, request, sid=None):

        adv_datas_list = list(VslDetail.objects.filter(specialist_status=True).values_list('dossier__id', flat=True))
        # print(adv_datas_list)
        datas = DossierData.objects.filter(id__in=adv_datas_list, source=SourceType.VslOptin).order_by('-id')

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
            gcs_folder_name = "media/source/pdf"
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
        if str(source_type) == "18":
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
                    "total_questions":'Created At',
                    "document_status":'Document Status',
                    "referral_code":'Referral Code',
                    "referred_code":'Referred Code',
                    "program":'Program',
                    "reffered_by":'Referred By'
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
                    "total_questions":chapter_data['created_at'],
                    "document_status":chapter_data['document_status'],
                    "referral_code":chapter_data['referral_code'],
                    "referred_code":chapter_data['referred_code'],
                    "program":chapter_data['program'],
                    "reffered_by":chapter_data['reffered_by']
                })
        else:
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
                    "total_questions":'',
                    "document_status":'',
                    "referral_code":'',
                    "referred_code":''
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
                    "total_questions":'',
                    "document_status":'',
                    "referral_code":'',
                    "referred_code":''
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
                    "total_questions":'Created At',
                    "document_status":'Document Status',
                    "referral_code":'Referral Code',
                    "referred_code":'Referred Code'
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
                    "total_questions":chapter_data['created_at'],
                    "document_status":chapter_data['document_status'],
                    "referral_code":chapter_data['referral_code'],
                    "referred_code":chapter_data['referred_code']
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

class GetVSLAdvisorReportExcelView(APIView):
    # permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"full_name","email","phone","city","state"]
    ordering_fields = ['id',"full_name","email","phone","city","state","created_at"]

    def get(self, request, sid=None):
        
        adv_datas_list = list(VslDetail.objects.filter(specialist_status=True).values_list('dossier__id', flat=True))
        # print(adv_datas_list)
        datas = DossierData.objects.filter(id__in=adv_datas_list, source=SourceType.VslOptin).order_by('-id')

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
        # d_list = [519,313,506,404,387,489,505,509]
        # d_list = [5562,5561,5403,4547,4554,4553,4509,4508,4506,427,426,425]
        # d_list = [6117,2328,3377,6376,1013,6373,6375,248,3268,4450,4614,6337,251,272,961,962,2823,3610,3807,4341,4628,5555,5724,5899,6374,6372,6370,6366,6362,5315,6379,6377,6500,6499,6498,6513,6931,6536,6554,6471]
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



















###################### Extra ###################
from openpyxl import Workbook
from openpyxl.styles import Font
# from django.http import HttpResponse
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
import uuid

# class ExcelLogicProcessAPI(APIView):

#     def post(self, request, *args, **kwargs):
#         print("starting...")
#         file = request.FILES.get("file")
#         print("starting...1")

#         if not file:
#             return Response(
#                 {"error": "Excel file is required"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         print("dd")
#         try:
#             # =========================
#             # READ EXCEL FILE
#             # =========================
#             df = pd.read_csv(file)
#             # print(df)
#             # =========================
#             # VALIDATE REQUIRED COLUMN
#             # =========================
#             required_columns = [
#                 "Registered Name",
#                 "Registered Email",
#                 "Registered Mobile"
#             ]

#             print("starting...2")
#             missing_columns = [
#                 col for col in required_columns
#                 if col not in df.columns
#             ]

#             if missing_columns:
#                 return Response(
#                     {
#                         "error": f"Missing columns: {missing_columns}"
#                     },
#                     status=400
#                 )

#             # =========================
#             # CLEAN DATA
#             # =========================
#             df["Registered Mobile"] = (
#                 df["Registered Mobile"]
#                 .astype(str)
#                 .str.replace("+91", "", regex=False)
#                 .str.replace("-", "", regex=False)
#                 .str.replace(" ", "", regex=False)
#                 .str.replace("`", "", regex=False)
#                 .str.strip()
#             )

#             df["Registered Email"] = (
#                 df["Registered Email"]
#                 .astype(str)
#                 .str.lower()
#                 .str.strip()
#             )

#             # =========================
#             # REMOVE DUPLICATES
#             # =========================
#             df.drop_duplicates(
#                 subset=["Registered Mobile"],
#                 keep="first",
#                 inplace=True
#             )
#             print(df)
#             # =========================
#             # LOGIC PROCESS
#             # =========================
#             updated_data = []

#             for _, row in df.iterrows():

#                 mobile = row["Registered Mobile"]
#                 email = row["Registered Email"]
#                 print(mobile)
#                 print(email)



#             #     # Match with database
#             #     lead = DossierData.objects.filter(
#             #         mobile__icontains=mobile
#             #     ).first()

#             #     if lead:
#             #         status_value = "EXISTING LEAD"
#             #         db_email = lead.email
#             #     else:
#             #         status_value = "NEW LEAD"
#             #         db_email = ""

#                 updated_data.append({
#                     "Registered Name": row["Registered Name"],
#                     "Registered Email": email,
#                     "Registered Mobile": mobile
#                 })

#             # =========================
#             # CREATE OUTPUT EXCEL
#             # =========================
#             wb = Workbook()
#             ws = wb.active
#             ws.title = "Processed Data"

#             headers = [
#                 "Registered Name",
#                 "Registered Email",
#                 "Registered Mobile"
#             ]

#             # Add Header
#             for col_num, header in enumerate(headers, 1):
#                 cell = ws.cell(row=1, column=col_num)
#                 cell.value = header
#                 cell.font = Font(bold=True)

#             # Add Rows
#             for row_num, item in enumerate(updated_data, 2):
#                 ws.cell(row=row_num, column=1).value = item["Registered Name"]
#                 ws.cell(row=row_num, column=2).value = item["Registered Email"]
#                 ws.cell(row=row_num, column=3).value = item["Registered Mobile"]

#             # =========================
#             # RETURN EXCEL RESPONSE
#             # =========================
#             output = BytesIO()
#             wb.save(output)
#             output.seek(0)

#             with tempfile.NamedTemporaryFile(
#                 suffix='.xlsx',
#                 delete=False
#             ) as temp_file:

#                 excel_path = temp_file.name

#                 output_df = pd.DataFrame(updated_data)

#                 output_df.to_excel(
#                     excel_path,
#                     index=False
#                 )

#             try:

#                 # =========================
#                 # GCP STORAGE UPLOAD
#                 # =========================

#                 timestamp = datetime.now().strftime(
#                     "%d_%m_%Y_%H_%M_%S"
#                 )

#                 report_name = "processed_leads"

#                 gcs_folder_name = (
#                     "media/reports/excel"
#                 )

#                 gcs_file_name = (
#                     f"{gcs_folder_name}/"
#                     f"{report_name}_{timestamp}.xlsx"
#                 )

#                 # Initialize GCP Client
#                 client = storage.Client()

#                 # Bucket
#                 bucket = client.get_bucket(
#                     settings.GS_BUCKET_NAME
#                 )

#                 # Blob
#                 blob = bucket.blob(gcs_file_name)

#                 # Upload File
#                 blob.upload_from_filename(excel_path)

#                 # Public URL
#                 file_url = blob.public_url

#                 # =========================
#                 # RESPONSE
#                 # =========================
#                 return Response(
#                     {
#                         "status": True,
#                         "message": "Excel processed successfully",
#                         "file_url": file_url
#                     },
#                     status=status.HTTP_200_OK
#                 )

#             finally:

#                 # Delete Temp File
#                 if os.path.exists(excel_path):
#                     os.remove(excel_path)

#         except Exception as e:
#             return Response(
#                 {"error": str(e)},
#                 status=500
#             )



import os
import pandas as pd
import tempfile
from datetime import datetime
from google.cloud import storage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings


class ExcelLogicProcessAPI(APIView):

    def post(self, request, *args, **kwargs):

        try:

            file = request.FILES.get("file")

            if not file:
                return Response(
                    {"error": "Excel file is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # =========================
            # READ FILE
            # =========================
            file_name = file.name.lower()

            if file_name.endswith(".csv"):
                df = pd.read_csv(file)

            elif file_name.endswith(".xlsx"):
                df = pd.read_excel(file, engine="openpyxl")

            else:
                return Response(
                    {"error": "Only CSV/XLSX files allowed"},
                    status=400
                )

            # =========================
            # VALIDATE REQUIRED COLUMNS
            # =========================
            required_columns = [
                "Registered Name",
                "Registered Email",
                "Registered Mobile"
            ]

            missing_columns = [
                col for col in required_columns
                if col not in df.columns
            ]

            if missing_columns:
                return Response(
                    {
                        "error": f"Missing columns: {missing_columns}"
                    },
                    status=400
                )

            # =========================
            # CLEAN DATA
            # =========================
            df["Registered Mobile"] = (
                df["Registered Mobile"]
                .astype(str)
                .str.replace("+91", "", regex=False)
                .str.replace("-", "", regex=False)
                .str.replace(" ", "", regex=False)
                .str.replace("`", "", regex=False)
                .str.strip()
            )

            df["Registered Email"] = (
                df["Registered Email"]
                .astype(str)
                .str.lower()
                .str.strip()
            )

            # =========================
            # REMOVE DUPLICATES
            # =========================
            df.drop_duplicates(
                subset=["Registered Mobile"],
                keep="first",
                inplace=True
            )

            # =========================
            # APPLY LOGIC
            # =========================
            updated_data = []

            for _, row in df.iterrows():

                mobile = row["Registered Mobile"]
                email = row["Registered Email"]
                # if mobile and email:
                print(mobile, email)
                if (str(mobile).upper() != "NA") & (str(email).upper() != "NA"):
                    
                # =========================
                # YOUR DB LOGIC
                # =========================

                # lead = DossierData.objects.filter(
                #     mobile__icontains=mobile
                # ).first()

                # if lead:
                #     lead_status = "EXISTING"
                # else:
                #     lead_status = "NEW"

                    updated_data.append({
                        "Registered Name": row["Registered Name"],
                        "Registered Email": email,
                        "Registered Mobile": mobile,
                    })

            # =========================
            # CREATE TEMP EXCEL FILE
            # =========================
            with tempfile.NamedTemporaryFile(
                suffix='.xlsx',
                delete=False
            ) as temp_file:

                excel_path = temp_file.name

                output_df = pd.DataFrame(updated_data)

                output_df.to_excel(
                    excel_path,
                    index=False
                )

            try:

                # =========================
                # GCP STORAGE UPLOAD
                # =========================

                timestamp = datetime.now().strftime(
                    "%d_%m_%Y_%H_%M_%S"
                )

                report_name = "processed_leads"

                gcs_folder_name = (
                    "media/reports/excel"
                )

                gcs_file_name = (
                    f"{gcs_folder_name}/"
                    f"{report_name}_{timestamp}.xlsx"
                )

                # Initialize GCP Client
                client = storage.Client()

                # Bucket
                bucket = client.get_bucket(
                    settings.GS_BUCKET_NAME
                )

                # Blob
                blob = bucket.blob(gcs_file_name)

                # Upload File
                blob.upload_from_filename(excel_path)

                # Public URL
                file_url = blob.public_url

                # =========================
                # RESPONSE
                # =========================
                return Response(
                    {
                        "status": True,
                        "message": "Excel processed successfully",
                        "file_url": file_url
                    },
                    status=status.HTTP_200_OK
                )

            finally:

                # Delete Temp File
                if os.path.exists(excel_path):
                    os.remove(excel_path)

        except Exception as e:

            return Response(
                {
                    "status": False,
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




##########################################################################################################
### testing ###

import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ImportEmailView(APIView):

    def post(self, request):
        excel_file = request.FILES.get("file")

        if not excel_file:
            return Response(
                {"message": "Please upload an Excel file."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Read Excel
            # df = pd.read_excel(excel_file)
            df = pd.read_csv(excel_file)

            # Check column exists
            if "Registered Email" not in df.columns:
                return Response(
                    {"message": "Registered Email column not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get emails
            emails = (
                df["Registered Email"]
                .dropna()
                .astype(str)
                .str.strip()
                .tolist()
            )

            # # print(emails)
            # j = 0
            # # all_data = list(DossierData.objects.all().values_list('email', flat=True))
            # all_data = list(User.objects.all().values('email','application_id'))
            # # all_data = User.objects.all().values('email','application_id')
            # for i in emails:
            #     for k in all_data:
            #         if i.lower() == str(k["email"]).lower():
            #             print(k)
            #             j+=1
                        
            #             url = settings.MERITO_BASE_URL+"/lead/v1/createOrUpdate"
            #             headers = {
            #                 "Content-Type": "application/json",
            #                 "secret-key": settings.MERITO_SECRETE_KEY,
            #                 "access-key": settings.MERITO_ACCESS_KEY
            #             }
            #             payload = {
            #                 "email": i.lower(),
            #                 "search_criteria": "email",
            #                 "cf_gcc_application_number":k["application_id"]
            #             }
            #             try:
            #                 response = requests.post(url, headers=headers, json=payload)
            #                 print(response.status_code)
            #                 print(response.text)
            #             except Exception as e:
            #                 print("API Error:", str(e))

            #         # j+=1

            # print(j)

            headers = {
                "Content-Type": "application/json",
                "secret-key": settings.MERITO_SECRETE_KEY,
                "access-key": settings.MERITO_ACCESS_KEY
            }

            # all_users = {
            #         str(user["email"]).lower(): user["application_id"]
            #         for user in User.objects.exclude(email__isnull=True)
            #         .values("email", "application_id")
            #     }
            all_data = list(DossierData.objects.all().values_list('email', flat=True))
            matched_count = 0
            l = 0
            for email in emails:
                # ee = all_users.get(email.lower())
                # print(type(ee))
                # if str(email).lower() in all_data:
                payload = {
                    "email": str(email).lower(),
                    "search_criteria": "email",
                    "cf_payment_status":"Pending"
                }

                try:
                    response = requests.post(
                        settings.MERITO_BASE_URL + "/lead/v1/createOrUpdate",
                        headers=headers,
                        json=payload,
                        timeout=30
                    )

                    print(email, response.status_code)
                    l+=1
                except Exception as e:
                    print(f"{email}: {str(e)}")

                matched_count+=1
                print(matched_count)
                
            return Response({
                "message": "Success",
                "total_emails": len(emails),
                "total_website_emails": matched_count,
                "l":l,
                "emails": emails
            })

        except Exception as e:
            return Response(
                {"message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


### for affliate 6 data export ##############


class GetDossierAffliateSixReportExcelView(APIView):
    def get(self, request, sid=None):
        # datas = DossierData.objects.filter(source=SourceType.Affiliate6).order_by('-id')
        datas = (DossierData.objects.filter(source=SourceType.Affiliate6).order_by('phone', '-id').distinct('phone'))
        # print(len(datas))
        # return Response({})
        data_list = ListDossierDataAffliateSixReportSerializer(datas, many=True).data
        COLUMN_MAPPING = {
            "full_name":'Full Name',
            "email":'Email',
            "phone":'Phone',
            "city":'City',
            "state":'State',
            "fbc_id":'FBC ID',
            "utm_source":'UTM SOURCE',
            "utm_medium":'UTM MEDIUM',
            "utm_content":'UTM CONTENT',
            "utm_campaign":'UTM CAMPAIGN',
            "campaign_id":'CAMPAIGN ID',
            "utm_adname":'UTM ADNAME',
            "adset_id":'ADSET ID',
            "fbclid":'FBCLID',
            "ad_source":'AD SOURCE',
            "ad_id":'AD ID',
            "fee_waiver_category":'FEE WAIVER CATEGORY',
            "created_at":'CREATE TIMESTAMP'
        }
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            pdf_path = temp_file.name

            df = pd.DataFrame(data_list)
            # df = df.drop_duplicates(
            #     subset=['phone'],
            #     keep='first'
            # )
            df = df[list(COLUMN_MAPPING.keys())]

            df.rename(columns=COLUMN_MAPPING, inplace=True)

            df.to_excel(
                pdf_path,
                header=True,
                index=False
            )
        try:
            # GCS file naming logic
            timestamp = datetime.now().strftime("%d_%m_%y_%H_%M")
            report_name = "lead_report"
            gcs_folder_name = "media/reports/dossier/excel/affliatesix"
            gcs_file_name = f"{gcs_folder_name}/{report_name}.xlsx"

            # Upload the temporary file to GCS
            bucket = client.get_bucket(settings.GS_BUCKET_NAME)
            blob = bucket.blob(gcs_file_name)
            # overwrite existing file
            # if blob.exists():
            #     blob.delete(igno)
                # blob.upload_from_filename(pdf_path)

            # upload new excel
            # blob.upload_from_filename(
            #     pdf_path,
            #     content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            # )
            # blob.reload()
            # print(blob.updated)
            # print("updated:", blob.updated)
            # print("generation:", blob.generation)
            blob = bucket.blob(gcs_file_name)

            blob.upload_from_filename(
                pdf_path,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            blob.cache_control = "no-cache"
            blob.patch()

            print(blob.updated)
            return success_response(
                message="Success",
                data={"report_url": blob.public_url},
                status_code=status.HTTP_200_OK
            )
        finally:
            # Ensure the temporary file is deleted
            os.remove(pdf_path)




import pandas as pd
from django.http import HttpResponse


import pandas as pd
from django.http import HttpResponse
from io import BytesIO
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment


class GetDossierAffliateSixReportExcelView(APIView):

    def get(self, request, sid=None):

        datas = (
            DossierData.objects
            .filter(source=SourceType.Affiliate6)
            .order_by('id')
        )

        # remove duplicate phone
        seen = set()
        unique_data = []

        for item in datas:
            if item.phone not in seen:
                seen.add(item.phone)
                unique_data.append(item)


        data_list = ListDossierDataAffliateSixReportSerializer(
            unique_data,
            many=True
        ).data


        COLUMN_MAPPING = {
            "full_name": 'Full Name',
            "email": 'Email',
            "phone": 'Phone',
            "city": 'City',
            "state": 'State',
            "fbc_id": 'FBC ID',
            "utm_source": 'UTM SOURCE',
            "utm_medium": 'UTM MEDIUM',
            "utm_content": 'UTM CONTENT',
            "utm_campaign": 'UTM CAMPAIGN',
            "campaign_id": 'CAMPAIGN ID',
            "utm_adname": 'UTM ADNAME',
            "adset_id": 'ADSET ID',
            "fbclid": 'FBCLID',
            "ad_source": 'AD SOURCE',
            "ad_id": 'AD ID',
            "fee_waiver_category": 'FEE WAIVER CATEGORY',
            "created_at": 'CREATE TIMESTAMP'
        }


        df = pd.DataFrame(data_list)


        df = df[list(COLUMN_MAPPING.keys())]


        df.rename(
            columns=COLUMN_MAPPING,
            inplace=True
        )


        # create excel in memory
        excel_file = BytesIO()

        df.to_excel(
            excel_file,
            index=False
        )

        excel_file.seek(0)


        # format excel
        wb = load_workbook(excel_file)
        ws = wb.active


        # header style
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(
                horizontal="center"
            )


        # auto width
        for column in ws.columns:

            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:
                if cell.value:
                    max_length = max(
                        max_length,
                        len(str(cell.value))
                    )

            ws.column_dimensions[column_letter].width = max_length + 5


        response = HttpResponse(
            content_type=
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        response["Content-Disposition"] = (
            'attachment; filename="lead_report.xlsx"'
        )


        wb.save(response)


        return response



class GetDossierInterviewAffliateSevenReportExcelView(APIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["full_name","email","phone","city","state","interview_date"]
    ordering_fields = ['id']

    def get(self, request, sid=None):
        
        datas = DossierData.objects.filter(source=SourceType.Affiliate7).order_by('-id')

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

        serializers = ListDossierDataAffliateSevenInterviewSerializer(datas, many=True)

        lis = []
        
        lis.append({
                "full_name":"Dossier Interview Report",
                "email":'',
                "phone":'',
                "interview_date":'',
                "created_at":''
            })

       
        lis.append({
                "full_name":"",
                "email":'',
                "phone":'',
                "interview_date":'',
                "created_at":''
            })
        
        lis.append({
                "full_name":"Full Name",
                "email":'Email',
                "phone":'Phone Number',
                "interview_date":'Interview Date',
                "created_at":'Register Date&Time'
            })
        
        
        for chapter_data in serializers.data:
            lis.append({
                "full_name":chapter_data['full_name'],
                "email":chapter_data['email'],
                "phone":chapter_data['phone'],
                "interview_date":chapter_data['interview_date'],
                "created_at":chapter_data['created_at'],
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
            report_name = "dossier_interview_report"
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








##########################

from utils.google_sheet import get_google_sheet


class GetAffliateSixExcelView(APIView):
    def post(self, request, sid=None):

        sheet = get_google_sheet()

        # row = [
        #     dossier.get("full_name"),
        #     dossier.get("email"),
        #     dossier.get("phone"),
        #     dossier.get("city"),
        #     dossier.get("state"),
        #     dossier.get("created_at"),
        # ]
        {
            "full_name": 'Full Name',
            "email": 'Email',
            "phone": 'Phone',
            "city": 'City',
            "state": 'State',
            "fbc_id": 'FBC ID',
            "utm_source": 'UTM SOURCE',
            "utm_medium": 'UTM MEDIUM',
            "utm_content": 'UTM CONTENT',
            "utm_campaign": 'UTM CAMPAIGN',
            "campaign_id": 'CAMPAIGN ID',
            "utm_adname": 'UTM ADNAME',
            "adset_id": 'ADSET ID',
            "fbclid": 'FBCLID',
            "ad_source": 'AD SOURCE',
            "ad_id": 'AD ID',
            "fee_waiver_category": 'FEE WAIVER CATEGORY',
            "created_at": 'CREATE TIMESTAMP'
        }
        # row = [
        #     obj.full_name,
        #     obj.email,
        #     obj.phone,
        #     obj.city,
        #     obj.state,
        #     obj.fbc_id,
        #     obj.utm_source,
        #     obj.utm_medium,
        #     obj.utm_content,
        #     obj.utm_campaign,
        #     obj.campaign_id,
        #     obj.utm_adname,
        #     obj.adset_id,
        #     obj.fbclid,
        #     obj.ad_source,
        #     obj.ad_id,
        #     obj.fee_waiver_category,
        #     obj.created_at
        # ]
        
        

        # sheet.append_row(row)


        return success_response(
                message="Success",
                data={"report_url": ""},
                status_code=status.HTTP_200_OK
            )


class GetAffliateSevenLeadAllReportExcelView(APIView):
    # permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['id',"full_name","email","phone","city","state"]
    ordering_fields = ['id',"full_name","email","phone","city","state","created_at"]

    def get(self, request, sid=None):
        
        datas = DossierData.objects.filter(source=SourceType.Affiliate7).order_by('id')
        # remove duplicate phone
        seen = set()
        unique_data = []

        for item in datas:
            if item.phone not in seen:
                seen.add(item.phone)
                unique_data.append(item)

        serializers = ListDossierDataAffliateSevenInterviewLiveReportSerializer(unique_data, many=True)

        lis = []
        
        lis.append({
                "full_name":"Dossier Report",
                "email":'',
                "phone":'',
                "city":'',
                "state":'',
                "interview_booked_status":'',
                "interview_date":'',
                "created_at":''
            })

       
        lis.append({
                "full_name":"Dossier Report",
                "email":'',
                "phone":'',
                "city":'',
                "state":'',
                "interview_booked_status":'',
                "interview_date":'',
                "created_at":''
            })
        
        lis.append({
                "full_name":"full name",
                "email":'Email',
                "phone":'Phone',
                "city":'City',
                "state":'State',
                "interview_booked_status":'status',
                "interview_date":'interview date',
                "created_at":'Created_at'
            })
        
        
        for chapter_data in serializers.data:
            lis.append({
                "full_name":chapter_data['full_name'],
                "email":chapter_data['email'],
                "phone":chapter_data['phone'],
                "city":chapter_data['city'],
                "state":chapter_data['state'],
                "interview_booked_status":chapter_data['interview_booked_status'],
                "interview_date":chapter_data['interview_date'],
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




