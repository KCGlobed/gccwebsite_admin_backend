from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from gcc_backend.utils import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from career.models import ProgramType
from django.db.models import Count, Q

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
    


## dashboard ##


from datetime import datetime, date
from gcc_backend.utils import parse_date

class DashboardAnalytics(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        start_date = request.GET.get("start_date")
        end_date   = request.GET.get("end_date")
        if start_date:
            start_date = parse_date(start_date)
        else:
            start_date = datetime.now().date() - timedelta(days=30)

        if end_date:
            end_date = parse_date(end_date)
        else:
            end_date = datetime.now().date()

        result = {}

        # Subquery instead of loading emails into Python
        lead_emails = DossierData.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).values("email").distinct()

        # Total leads
        result["lead_count"] = DossierData.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).count()

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
        return success_response(message="Success",data=result,status_code=status.HTTP_200_OK)


class DashboardLeadAnalytics(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        start_date = request.GET.get("start_date")
        end_date   = request.GET.get("end_date")
        if start_date:
            start_date = parse_date(start_date)
        else:
            start_date = datetime.now().date() - timedelta(days=30)

        if end_date:
            end_date = parse_date(end_date)
        else:
            end_date = datetime.now().date()

        result = {}
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
        
        state_data = DossierData.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).values('state').annotate(count=Count('id')).order_by('-count')[:10]
        result["state_wise_leads"] = state_data
        
        fee_waiver_data = DossierData.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).aggregate(
            total_lead_percent=Count("id"),
            no_waive_percent=Count("id", filter=Q(fee_waiver_category='No Waiver')),
            foc_percent=Count("id", filter=Q(fee_waiver_category='Free of cost (FOC)')),
            cpa_enrolled=Count("id", filter=Q(program=ProgramType.CPA)),
            ea_enrolled=Count("id", filter=Q(program=ProgramType.EA)),
            other_enrolled=Count("id", filter=Q(program=None)),
            )
        
        total = int(fee_waiver_data.get("total_lead_percent") or 0)
        
        waiver_data = {}
        # waiver_data["no_waive_percent"] = round(int(fee_waiver_data["no_waive_percent"])/int(fee_waiver_data["total_lead_percent"]) * 100, 2)
        waiver_data["no_waive_percent"] = (round(int(fee_waiver_data.get("no_waive_percent") or 0) / total * 100, 2)if total else 0)
        waiver_data["foc_percent"] = (round(int(fee_waiver_data.get("foc_percent") or 0) / total * 100, 2)if total else 0)
        waiver_data["total_lead_percent"] = 100.0
        result["fee_waiver_stats"] = waiver_data

        program_data = {}
        program_data["cpa_percent"] = (round(int(fee_waiver_data.get("cpa_enrolled") or 0) / total * 100, 2)if total else 0)
        program_data["ea_percent"] = (round(int(fee_waiver_data.get("ea_enrolled") or 0) / total * 100, 2)if total else 0)
        program_data["other_percent"] = (round(int(fee_waiver_data.get("other_enrolled") or 0) / total * 100, 2)if total else 0)
        result["program_stats"] = program_data
        
        university_data = DossierData.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).values('university').annotate(count=Count('id')).order_by('-count')[:10]
        result["university_wise_leads"] = university_data

        referred_data = DossierData.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).filter(Q(referred_code__isnull=False) & ~Q(referred_code="")).values('referred_code').annotate(count=Count('id')).order_by('-count')[:10]
        result["top_referred_leads"] = referred_data
        return success_response(message="Success", data=result, status_code=status.HTTP_200_OK)



class DashboardProfileAnalytics(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        start_date = request.GET.get("start_date")
        end_date   = request.GET.get("end_date")
        if start_date:
            start_date = parse_date(start_date)
        else:
            start_date = datetime.now().date() - timedelta(days=30)

        if end_date:
            end_date = parse_date(end_date)
        else:
            end_date = datetime.now().date()

        result = {}
        state_data = StudentProfile.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).values('state').annotate(count=Count('id')).order_by('-count')[:10]
        result["profile_state_wise_data"] = state_data
        profile_waiver_data = StudentProfile.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).aggregate(
            total_percent=Count('id'),
            no_waive_percent=Count('id', filter=Q(fee_waiver_category='No Waiver')),
            foc_percent=Count('id', filter=Q(fee_waiver_category='Free of cost (FOC)')),
            fresher_percent=Count('id', filter=Q(employement_status=EmployementStatus.FRESHER)),
            experience_percent=Count('id', filter=Q(employement_status=EmployementStatus.EXPERIENCED)),
            persue_percent=Count('id', filter=Q(pg_status=PGStatus.PURSURING)),
            complete_percent=Count('id', filter=Q(pg_status=PGStatus.COMPLETED)),
            mgender_percent=Count('id', filter=Q(gender=Gender.MALE)),
            fgender_percent=Count('id', filter=Q(gender=Gender.FEMALE)),
            ogender_percent=Count('id', filter=Q(gender=Gender.OTHER)),
            higher_percent=Count('id', filter=Q(higher_education_status=HigherEducation.YES)),
            non_higher_percent=Count('id', filter=Q(higher_education_status=HigherEducation.NO)),
        )
        total = int(profile_waiver_data.get("total_percent") or 0)
        waiver_data = {}
        waiver_data["no_waive_percent"] = (round(int(profile_waiver_data.get("no_waive_percent") or 0) / total * 100, 2)if total else 0)
        # waiver_data["no_waive_percent"] = round(int(profile_waiver_data["no_waive_percent"])/int(profile_waiver_data["total_percent"]) * 100, 2)
        waiver_data["foc_percent"] = (round(int(profile_waiver_data.get("foc_percent") or 0) / total * 100, 2)if total else 0)
        result["fee_waiver_stats"] = waiver_data

        employement_stats = {}
        employement_stats["fresher_percent"] = (round(int(profile_waiver_data.get("fresher_percent") or 0) / total * 100, 2)if total else 0)
        employement_stats["experience_percent"] = (round(int(profile_waiver_data.get("experience_percent") or 0) / total * 100, 2)if total else 0)
        result["employement_stats"] = employement_stats

        pg_stats = {}
        pg_stats["fresher_percent"] = (round(int(profile_waiver_data.get("persue_percent") or 0) / total * 100, 2)if total else 0)
        pg_stats["experience_percent"] = (round(int(profile_waiver_data.get("complete_percent") or 0) / total * 100, 2)if total else 0)
        pg_stats["total_percent"] = 100.0
        result["pg_stats"] = pg_stats

        gender_stats = {}
        gender_stats["male_percent"] = (round(int(profile_waiver_data.get("mgender_percent") or 0) / total * 100, 2)if total else 0)
        gender_stats["female_percent"] = (round(int(profile_waiver_data.get("fgender_percent") or 0) / total * 100, 2)if total else 0)
        gender_stats["other_percent"] = (round(int(profile_waiver_data.get("ogender_percent") or 0) / total * 100, 2)if total else 0)
        result["gender_stats"] = gender_stats

        higher_qualify_stats = {}
        higher_qualify_stats["higher_percent"] = (round(int(profile_waiver_data.get("higher_percent") or 0) / total * 100, 2)if total else 0)
        higher_qualify_stats["non_higher_percent"] = (round(int(profile_waiver_data.get("non_higher_percent") or 0) / total * 100, 2)if total else 0)
        result["higher_qualify_stats"] = higher_qualify_stats

        profile_metric_stats = {}
        profile_metric_stats["profiles"] = total
        profile_metric_stats["freshers"] = (round(int(profile_waiver_data.get("persue_percent") or 0) / total * 100, 2)if total else 0)
        profile_metric_stats["ug_done"] = (round(int(profile_waiver_data.get("complete_percent") or 0) / total * 100, 2)if total else 0)
        profile_metric_stats["higher_qualify"] = (round(int(profile_waiver_data.get("higher_percent") or 0) / total * 100, 2)if total else 0)
        profile_metric_stats["foc"] = (round(int(profile_waiver_data.get("foc_percent") or 0) / total * 100, 2)if total else 0)
        profile_metric_stats["male"] = (round(int(profile_waiver_data.get("mgender_percent") or 0) / total * 100, 2)if total else 0)
        result["profile_metric_stats"] = profile_metric_stats

        return success_response(message="Success", data=result, status_code=status.HTTP_200_OK)
    

class DashboardLeadProfileAnalytics(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        start_date = request.GET.get("start_date")
        end_date   = request.GET.get("end_date")
        if start_date:
            start_date = parse_date(start_date)
        else:
            start_date = datetime.now().date() - timedelta(days=30)

        if end_date:
            end_date = parse_date(end_date)
        else:
            end_date = datetime.now().date()

        result = {}
        lstate_data = DossierData.objects.filter(state__isnull=False, created_at__date__gte=start_date, created_at__date__lte=end_date).values('state').annotate(lead_count=Count('id')).order_by('-lead_count')[:10]
        profile_state_data = StudentProfile.objects.values('state').annotate(profile_count=Count('id')).order_by('-profile_count')
        lead_profile_stats = []
        for lead in list(lstate_data):
            count = profile_state_data.filter(state=lead["state"]).first()
            if count:
                num = count["profile_count"]
            else:
                num = 0
            lead["profile_count"] = num
            lead_profile_stats.append(lead)
        result["lead_profile_stats"] = lead_profile_stats

        return success_response(message="Success", data=result, status_code=status.HTTP_200_OK)
    

