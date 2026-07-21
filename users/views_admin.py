from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from gcc_backend.utils import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from datetime import date
from django.db.models import Count
from django.db.models.functions import TruncDate


class CreateUniversityStudentView(APIView):
    def post(self, request, format=None):
        serializer = CreateUniversityStudentSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            user  = serializer.save()
            # generated_password = serializer.generated_password
            return success_response(message="User Created Successfully", data={}, status_code=status.HTTP_200_OK)
        return error_response(message="failed", data = serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    




class VerifyRefferalCodeView(APIView):
    def post(self, request, format=None):
        code = request.data.get('refferal_code')
        statuss = False
        if ManageFreeReferal.objects.filter(free_referral_code=code).exists():
                statuss = True
                return success_response(message="success", data={"verified_status":statuss}, status_code=status.HTTP_200_OK)
        if User.objects.filter(referral_code=code).exists():
            user_obj = User.objects.filter(referred_code=code)
            if not user_obj:
                statuss = True
                return success_response(message="success", data={"verified_status":statuss}, status_code=status.HTTP_200_OK)
        return error_response(message="Invalid Code", data = {"verified_status":statuss}, status_code=status.HTTP_400_BAD_REQUEST)
    


import random
import string
def generate_referral_code():
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=20))




class AdminRoleListView(APIView):
    def get(self, request, format=None):
        role = [
            {
                "name":"Admin",
                "value":"SuperAdmin"
            },
            {
                "name":"EFOS",
                "value":"Efos"
            },
            {
                "name":"ET",
                "value":"Other"
            },
            {
                "name":"VSL",
                "value":"Vsl"
            },
            {
                "name":"AffliateOne",
                "value":"AffliateOne"
            },
            {
                "name":"AffliateTwo",
                "value":"AffliateTwo"
            },
            {
                "name":"AffliateThree",
                "value":"AffliateThree"
            },
            {
                "name":"AffliateFour",
                "value":"AffliateFour"
            },
            {
                "name":"AffliateFive",
                "value":"AffliateFive"
            },
            {
                "name":"AffliateSix",
                "value":"AffliateSix"
            },
            {
                "name":"AffliateSeven",
                "value":"AffliateSeven"
            },
            {
                "name":"EA LP",
                "value":"EAWebsite"
            },
            {
                "name":"CPA LP",
                "value":"CPAWebsite"
            },
        ]
        return success_response(message="Success", data=role, status_code=status.HTTP_200_OK)


class CreateStudentRefferalCodeView(APIView):
    def post(self, request, format=None):
        user = User.objects.all()
        for i in user:
            data = generate_referral_code()
            user_data = User.objects.filter(referral_code=data)
            if len(user_data) == 0 and not i.referral_code:
                i.referral_code = data
                i.save()
        return success_response(message="User Created Successfully", data={}, status_code=status.HTTP_200_OK)

from gcc_backend.utils import get_lower_reporting

class GetLowerReportingPerson(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        id = request.data.get("emp_id")
        data = get_lower_reporting(id)
        users_data = User.objects.filter(id__in=data).values("id","first_name","last_name","email","role")

        return success_response(message="Success", data={"list_data":users_data}, status_code=status.HTTP_200_OK)

class GetUpperReportingPerson(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        id = request.data.get("emp_id")
        data = get_upper_reporting(id)
        users_data = User.objects.filter(id__in=data).values("id","first_name","last_name","email","role")

        return success_response(message="Success", data={"list_data":users_data}, status_code=status.HTTP_200_OK)
    

class GetManageSalesPerson(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        users_data = User.objects.filter(role__in=[User.SalesPerson, User.SalesHead]).order_by('id')
        serialize = AdminProfileDetailSerializer(users_data, many=True)
        return success_response(message="Success", data={"list_data":serialize.data}, status_code=status.HTTP_200_OK)
    

class AssignedReportingEmployee(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serialize = ManageReportingAssignSerializer(data=request.data)
        return success_response(message="Success", data={"list_data":serialize.data}, status_code=status.HTTP_200_OK)
    

#######################

from datetime import timedelta
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
class DashboardAnalytics(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        result = {}

        # Subquery instead of loading emails into Python
        lead_emails = DossierData.objects.values("email").distinct()

        # Total leads
        result["lead_count"] = DossierData.objects.count()

        # Student statistics in a single query
        student_stats = StudentProfile.objects.filter(
            email__in=lead_emails
        ).aggregate(
            student_profile_count=Count("id"),
            foc_profile_count=Count(
                "id",
                filter=Q(fee_waiver_category="Free of cost (FOC)")
            ),
            ug_complete_count=Count(
                "id",
                filter=Q(pg_status=PGStatus.COMPLETED)
            ),
            fresher_profile_count=Count(
                "id",
                filter=Q(employement_status=EmployementStatus.FRESHER)
            ),
            higher_profile_count=Count(
                "id",
                filter=Q(higher_education_status=HigherEducation.YES)
            ),
        )

        result.update(student_stats)

        # Last 30 days lead chart
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        lead_data = (
            DossierData.objects
            .filter(created_at__date__range=(start_date, end_date))
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        lead_dict = {item["day"]: item["count"] for item in lead_data}

        result["monthly_leads"] = [
            {
                "day": start_date + timedelta(days=i),
                "count": lead_dict.get(start_date + timedelta(days=i), 0),
            }
            for i in range((end_date - start_date).days + 1)
        ]
        
        


        return success_response(message="Success",data=result,status_code=status.HTTP_200_OK)
    

# class DashboardAnalytics(APIView):
#     # permission_classes = [IsAuthenticated]
#     def get(self, request, format=None):
#         result = {}
#         lead_objs = list(DossierData.objects.all().values_list('email',flat=True))
#         std_objs = StudentProfile.objects.filter(email__in=lead_objs).values('id','email','fee_waiver_category','pg_status','employement_status','higher_education_status')
        
#         result["lead_count"] = len(lead_objs)
#         result["student_profile_count"] = std_objs.count()
#         result["foc_profile_count"] = std_objs.filter(fee_waiver_category='Free of cost (FOC)').count()
#         result["ug_complete_count"] = std_objs.filter(pg_status=PGStatus.COMPLETED).count()
#         result["fresher_profile_count"] = std_objs.filter(employement_status=EmployementStatus.FRESHER).count()
#         result["higher_profile_count"] = std_objs.filter(higher_education_status=HigherEducation.YES).count()

#         start_date = datetime.now().date() - timedelta(days=30)
#         end_date = datetime.now().date()
#         lead_data = DossierData.objects.filter(created_at__date__range=(start_date, end_date)).annotate(day=TruncDate('created_at')).values('day').annotate(count=Count('id')).order_by('day')
        
#         # Convert queryset to dictionary
#         lead_dict = {
#             item["day"]: item["count"]
#             for item in lead_data
#         }

#         # Fill missing dates with 0
#         result_list = []
#         current_date = start_date

#         while current_date <= end_date:
#             result_list.append({
#                 "day": current_date,
#                 "count": lead_dict.get(current_date, 0)
#             })
#             current_date += timedelta(days=1)

#         print(result_list)
#         result["monthly_leads"] = result_list

#         return success_response(message="Success", data=result, status_code=status.HTTP_200_OK)
    




