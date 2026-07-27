from rest_framework import serializers
from .models import *
from django.conf import settings
from users.models import User
from students.models import StudentProfile, ManageStudentInterview
from users.serializers import StudentProfileDetailSerializer
import requests
from django.utils import timezone
from utils.google_sheet import get_google_sheet, get_google_sheet_affliate_seven

class ListCareerApplicationSerializer(serializers.ModelSerializer):
    resume_path = serializers.SerializerMethodField('get_resume_path')
    class Meta:
        model = CareerApplication
        fields = "__all__"
    
    def get_resume_path(self, obj):
        url = f'https://storage.googleapis.com/{settings.GS_BUCKET_NAME}/{obj.resume_path}'
        return url

class ListPartnerWithUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerWithUs
        fields = "__all__"
        


class CreateDossierDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierData
        # fields = ["full_name","email","phone","city","state","source","source_form"]
        fields = "__all__"
        
    def create(self, validated_data):
        instance = super().create(validated_data)
        if settings.MERITO_STATUS == "True":
            src_type = instance.source
            if src_type == 1:
                m_source = "gccwebsite"
            elif src_type == 2:
                m_source = "gccefos"
            elif src_type == 3:
                m_source = "gccaffiliateOne"
            elif src_type == 4:
                m_source = "gccaffiliateTwo"
            elif src_type == 5:
                m_source = "gccaffiliateThree"
            elif src_type == 6:
                m_source = "gccaffiliateFour"
            elif src_type == 7:
                m_source = "gccaffiliateFive"
            elif src_type == 8:
                m_source = "gccipuniversity"
            elif src_type == 9:
                m_source = "gccdelhiuniversity"
            elif src_type == 10:
                m_source = "gccccs"
            elif src_type == 11:
                m_source = "gcckuk"
            elif src_type == 14:
                m_source = "gccaffiliateSix"
            elif src_type == 15:
                m_source = "gccaffiliateSeven"
            elif src_type == 16:
                m_source = "gcccpa"
            elif src_type == 17:
                m_source = "gccea"
            elif src_type == 18:
                m_source = "gcceaWebsite"
            elif src_type == 19:
                m_source = "gcccpaWebsite"
            else:
                m_source = "gcc"
            # API URL
            url = settings.MERITO_BASE_URL+"/lead/v1/createOrUpdate"

            headers = {
                "Content-Type": "application/json",
                "secret-key": settings.MERITO_SECRETE_KEY,
                "access-key": settings.MERITO_ACCESS_KEY
            }

            payload = {
                "name": instance.full_name,
                "email": instance.email,
                "mobile": instance.phone,
                # "lead_stage": "hot",
                "search_criteria": "email",
                "city": instance.city,
                "state": instance.state,
                "country": "India",
                "source":m_source,
                "cf_source":m_source,
                # "cf_utmsource1":instance.utm_source,
                # "medium":instance.utm_medium,
                # "campaign":instance.utm_campaign,
                # "cf_utmsource1": str(instance.utm_source).encode("ascii", "ignore").decode().strip(),
                "medium": str(instance.utm_medium).encode("ascii", "ignore").decode().strip(),
                "campaign": str(instance.utm_campaign).encode("ascii", "ignore").decode().strip(),
                "cf_payment_status":"Pending",
                "cf_fee_waiver_category":instance.fee_waiver_category,
                "cf_institution_university":instance.university,
                # "cf_refferal_code":instance.get('referred_code')
            }

            user_obj = User.objects.filter(email=instance.email).exists()
            if user_obj:
                payload.pop('cf_payment_status')
                payload.pop('cf_fee_waiver_category')
            try:
                print("mer..",payload)
                response = requests.post(url, headers=headers, json=payload)
                print(response.status_code)
                print(response.text)
                DossierLog.objects.create(dossier=instance, message=response.text, status=int(response.status_code), activity="creating", datas=validated_data)
            except Exception as e:
                print("API Error:", str(e))


        ### for sheet 
        if settings.EXCEL_INPUT == "True":
            if src_type == 14:
                print("sheet enter")
                if not DossierData.objects.filter(phone=instance.phone, source=src_type).exclude(id=instance.id).exists():
                    print("valida data")
                    try:
                        sheet = get_google_sheet()
                        print("open sheet...",sheet)
                        local_time = timezone.localtime(instance.created_at)
                        create_times = local_time.strftime("%Y-%m-%d %H:%M:%S")
                        row = [
                            instance.full_name,
                            instance.email,
                            instance.phone,
                            instance.city,
                            instance.state,
                            instance.fbc_id,
                            instance.utm_source,
                            instance.utm_medium,
                            instance.utm_content,
                            instance.utm_campaign,
                            instance.campaign_id,
                            instance.utm_adname,
                            instance.adset_id,
                            instance.fbclid,
                            instance.ad_source,
                            instance.ad_id,
                            instance.fee_waiver_category,
                            create_times
                        ]
                        print("data inster",row)
                        sheet.append_row(row)
                        print("completed")
                    except Exception as e:
                        print("google sheet error", str(e))

        return instance


class CreateDossierDocumentSerializer(serializers.ModelSerializer):
    dossier_id = serializers.IntegerField(required=True)
    class Meta:
        model = DossierDocument
        fields = ["dossier_id","file"]


class CreateVslDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierData
        # fields = ["full_name","email","phone","degree","degree_stage","fbc_id","utm_source","utm_medium","utm_content","utm_campaign","utm_adname","campaign_id","adset_id","fbclid","ad_source","ad_id"]
        fields = "__all__"
        
    def create(self, validated_data):
        print(validated_data)
        validated_data['source'] = SourceType.VslOptin
        validated_data['source_form'] = SourceFormType.Program

        vsl_obj =  super().create(validated_data)

        # vsl_obj = DossierData(full_name=validated_data.get("full_name"), email=validated_data.get("email"),phone=validated_data.get("phone"),degree=validated_data.get("degree"),degree_stage=validated_data.get("degree_stage"),source=SourceType.VslOptin, source_form=SourceFormType.Program)
        # vsl_obj.save()

        if settings.MERITO_STATUS == "True":
            src_type = vsl_obj.source
            if src_type == 12:
                m_source = "gccvsloptin"
            else:
                m_source = "gcc"
            # API URL
            url = settings.MERITO_BASE_URL+"/lead/v1/createOrUpdate"

            headers = {
                "Content-Type": "application/json",
                "secret-key": settings.MERITO_SECRETE_KEY,
                "access-key": settings.MERITO_ACCESS_KEY
            }

            payload = {
                "search_criteria": "email",
                "name": vsl_obj.full_name,
                "email": vsl_obj.email,
                "mobile": vsl_obj.phone,
                # "lead_stage": "hot",
                # "cf_fee_waiver_category":"",
                # "search_criteria": "email",

                # "city": instance.city,
                # "state": instance.state,
                # "country": "India",
                
                "source":m_source,
                "cf_source":m_source,
                # "cf_utmsource1":vsl_obj.utm_source,
                # "medium":vsl_obj.utm_medium,
                # "campaign":vsl_obj.utm_campaign,
                # "cf_utmsource1": str(vsl_obj.utm_source).encode("ascii", "ignore").decode().strip(),
                "medium": str(vsl_obj.utm_medium).encode("ascii", "ignore").decode().strip(),
                "campaign": str(vsl_obj.utm_campaign).encode("ascii", "ignore").decode().strip(),
                "cf_payment_status":"Pending",
                "cf_fee_waiver_category":vsl_obj.fee_waiver_category,
                # "cf_refferal_code":vsl_obj.get('referred_code')
                # "cf_institution_university":vsl_obj.university
            }
            user_obj = User.objects.filter(email=vsl_obj.email).exists()
            if user_obj:
                payload.pop('cf_payment_status')
                payload.pop('cf_fee_waiver_category')

            print("meritto payload vslf..",payload)
            try:
                response = requests.post(url, headers=headers, json=payload)
                print(response.status_code)
                print(response.text)
                DossierLog.objects.create(dossier=vsl_obj, message=response.text, status=int(response.status_code), activity="creating", datas=validated_data)
            except Exception as e:
                print("API Error:", str(e))
        
        return vsl_obj



class CreateVslFinalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierData
        # fields = ["full_name","email","phone","city","state"]
        fields = "__all__"
        
    def create(self, validated_data):
        print(validated_data)
        validated_data['source'] = SourceType.VslFinal
        validated_data['source_form'] = SourceFormType.Dossier

        vsl_obj =  super().create(validated_data)
        # vsl_obj = DossierData(full_name=validated_data.get("full_name"), email=validated_data.get("email"),phone=validated_data.get("phone"),city=validated_data.get("city"),state=validated_data.get("state"),source=SourceType.VslFinal, source_form=SourceFormType.Dossier)
        # vsl_obj.save()

        if settings.MERITO_STATUS == "True":
            src_type = vsl_obj.source
            if src_type == 13:
                m_source = "gccvslfinal"
            else:
                m_source = "gcc"
            # API URL
            url = settings.MERITO_BASE_URL+"/lead/v1/createOrUpdate"

            headers = {
                "Content-Type": "application/json",
                "secret-key": settings.MERITO_SECRETE_KEY,
                "access-key": settings.MERITO_ACCESS_KEY
            }

            payload = {
                "name": vsl_obj.full_name,
                "email": vsl_obj.email,
                # "mobile": vsl_obj.phone,
                # "lead_stage": "hot",
                "search_criteria": "email",
                "city": vsl_obj.city,
                "state": vsl_obj.state,
                "country": "India",
                "source":m_source,
                "cf_source":m_source,
                # "cf_utmsource1":vsl_obj.utm_source,
                # "medium":vsl_obj.utm_medium,
                # "campaign":vsl_obj.utm_campaign,
                # "cf_utmsource1": str(vsl_obj.utm_source).encode("ascii", "ignore").decode().strip(),
                "medium": str(vsl_obj.utm_medium).encode("ascii", "ignore").decode().strip(),
                "campaign": str(vsl_obj.utm_campaign).encode("ascii", "ignore").decode().strip(),
                "cf_payment_status":"Pending",
                "cf_fee_waiver_category":vsl_obj.fee_waiver_category,
                "cf_institution_university":vsl_obj.university,
                # "cf_refferal_code":vsl_obj.referred_code
            }
            user_obj = User.objects.filter(email=vsl_obj.email).exists()
            if user_obj:
                payload.pop('cf_payment_status')
                payload.pop('cf_fee_waiver_category')
            try:
                response = requests.post(url, headers=headers, json=payload)
                print(response.status_code)
                print(response.text)
                DossierLog.objects.create(dossier=vsl_obj, message=response.text, status=int(response.status_code), activity="creating", datas=validated_data)
            except Exception as e:
                print("API Error:", str(e))
        
        return vsl_obj



class CreateVslOptinDetailDataSerializer(serializers.ModelSerializer):
    dossier_id = serializers.IntegerField(required=True)
    class Meta:
        model = VslDetail
        fields = ["dossier_id","video_playback"]
        
    def create(self, validated_data):
        vsl_obj = VslDetail.objects.filter(dossier_id=validated_data.get("dossier_id"))
        if vsl_obj:
            vsl_obj.update(video_playback=validated_data.get("video_playback"))
        else:
            vsl_obj = VslDetail(dossier_id=validated_data.get("dossier_id"), video_playback=validated_data.get("video_playback"))
            vsl_obj.save()

        return vsl_obj



class UpdateVslOptinDetailDataSerializer(serializers.ModelSerializer):
    dossier_id = serializers.IntegerField(required=True)
    class Meta:
        model = VslDetail
        fields = ["dossier_id","specialist_status"]
        
    def create(self, validated_data):
        vsl_obj = VslDetail.objects.filter(dossier_id=validated_data.get("dossier_id"))
        if vsl_obj:
            vsl_obj.update(specialist_status=validated_data.get("specialist_status"))
        else:
            vsl_obj = VslDetail(dossier_id=validated_data.get("dossier_id"), specialist_status=validated_data.get("specialist_status"))
            vsl_obj.save()

        return vsl_obj








class DossierDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierDocument
        fields = ["file"]


class ListDossierDataSerializer(serializers.ModelSerializer):
    # created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    created_at = serializers.SerializerMethodField()
    user_document_url = serializers.SerializerMethodField()
    document_status = serializers.SerializerMethodField('get_document_status')
    class Meta:
        model = DossierData
        fields = "__all__"
        
    def get_created_at(self, obj):
        if obj.created_at:
            local_time = timezone.localtime(obj.created_at)
            return local_time.strftime("%Y-%m-%d %H:%M:%S")
        return None

    def get_user_document_url(self, obj):
        user_obj = DossierDocument.objects.filter(dossier=obj.id)
        user_ser = DossierDocumentSerializer(user_obj, many=True).data
        return user_ser
    
    def get_document_status(self, obj):
        return obj.get_document_status_display()

class ListDossierDataAffliateSixReportSerializer(serializers.ModelSerializer):
    # created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    created_at = serializers.SerializerMethodField()
    class Meta:
        model = DossierData
        fields = "__all__"
        
    def get_created_at(self, obj):
        if obj.created_at:
            local_time = timezone.localtime(obj.created_at)
            return local_time.strftime("%Y-%m-%d %H:%M:%S")
        return None

    # def get_user_document_url(self, obj):
    #     user_obj = DossierDocument.objects.filter(dossier=obj.id)
    #     user_ser = DossierDocumentSerializer(user_obj, many=True).data
    #     return user_ser
    
    # def get_document_status(self, obj):
    #     return obj.get_document_status_display()

class ListNewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscribers
        fields = "__all__"
        

class CreateSupportFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportForm
        fields = ["subject","message"]

    def create(self, validated_data):
        request = self.context.get('request')   
        validated_data['user'] = request.user
        return super().create(validated_data)    



class ListSupportFormSerializer(serializers.ModelSerializer):
    user_detail = serializers.SerializerMethodField()
    class Meta:
        model = SupportForm
        fields = "__all__"

    def get_user_detail(self, obj):
        if obj.user:
            user_obj = User.objects.filter(id=obj.user.id)
            user_ser = StudentProfileDetailSerializer(user_obj, many=True).data
        else:
            user_ser = []
        return user_ser
        



class CreateDossierAbondantSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierAbondant
        fields = "__all__"

    def create(self, validated_data):
        instance = super().create(validated_data)
        if settings.MERITO_STATUS == "True":
            src_type = instance.source
            if src_type == 1:
                m_source = "gccwebsite"
            elif src_type == 2:
                m_source = "gccefos"
            elif src_type == 3:
                m_source = "gccaffiliateOne"
            elif src_type == 4:
                m_source = "gccaffiliateTwo"
            elif src_type == 5:
                m_source = "gccaffiliateThree"
            elif src_type == 6:
                m_source = "gccaffiliateFour"
            elif src_type == 7:
                m_source = "gccaffiliateFive"
            elif src_type == 8:
                m_source = "gccipuniversity"
            elif src_type == 9:
                m_source = "gccdelhiuniversity"
            elif src_type == 10:
                m_source = "gccccs"
            elif src_type == 11:
                m_source = "gcckuk"
            elif src_type == 12:
                m_source = "gccvsloptin"
            elif src_type == 13:
                m_source = "gccvslfinal"
            elif src_type == 14:
                m_source = "gccaffiliateSix"
            elif src_type == 16:
                m_source = "gcccpa"
            elif src_type == 17:
                m_source = "gccea"
            elif src_type == 18:
                m_source = "gcceaWebsite"
            else:
                m_source = "gcc"
            # API URL
            url = settings.MERITO_BASE_URL+"/lead/v1/createOrUpdate"

            headers = {
                "Content-Type": "application/json",
                "secret-key": settings.MERITO_SECRETE_KEY,
                "access-key": settings.MERITO_ACCESS_KEY
            }

            payload = {
                "name": instance.full_name,
                "email": instance.email,
                "mobile": instance.phone,
                # "lead_stage": "hot",
                "search_criteria": "email",
                # "city": instance.city,
                # "state": instance.state,
                # "country": "India",
                "source":m_source,
                "cf_source":m_source,
                # "cf_utmsource1":instance.utm_source,
                # "medium":instance.utm_medium,
                # "campaign":instance.utm_campaign,
                # "cf_utmsource1": str(instance.utm_source).encode("ascii", "ignore").decode().strip(),
                "medium": str(instance.utm_medium).encode("ascii", "ignore").decode().strip(),
                "campaign": str(instance.utm_campaign).encode("ascii", "ignore").decode().strip(),
                "cf_payment_status":"Pending"
                # "cf_fee_waiver_category":instance.fee_waiver_category
            }
            user_obj = User.objects.filter(email=instance.email).exists()
            if user_obj:
                payload.pop('cf_payment_status')
            try:
                response = requests.post(url, headers=headers, json=payload)
                print(response.status_code)
                print(response.text)
            except Exception as e:
                print("API Error:", str(e))
        return instance



class ListDossierAbondantSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = DossierAbondant
        fields = "__all__"
        





############### MERITTO UPLOAD BULK ################
import re

def push_to_meritto(obj):
    # if not settings.MERITO_STATUS:
    #     return

    source_map = {
        1: "gccwebsite",
        2: "gccefos",
        3: "gccaffiliateOne",
        4: "gccaffiliateTwo",
        5: "gccaffiliateThree",
        6: "gccaffiliateFour",
        7: "gccaffiliateFive",
        8: "gccipuniversity",
        9: "gccdelhiuniversity",
        10: "gccccs",
        11: "gcckuk",
        12: "gccvsloptin",
        13: "gccvslfinal",
        14: "gccaffiliateSix"
    }

    m_source = source_map.get(obj.source, "gcc")

    url = f"{settings.MERITO_BASE_URL}/lead/v1/createOrUpdate"

    headers = {
        "Content-Type": "application/json",
        "secret-key": settings.MERITO_SECRETE_KEY,
        "access-key": settings.MERITO_ACCESS_KEY
    }
    name = re.sub(r'[^\w\s]', '', obj.full_name).strip()
    payload = {
        "name": name,
        "email": obj.email,
        "mobile": obj.phone, 
        "search_criteria": "email",
        "country": "India",
        "source": m_source,
        # "cf_source": m_source,
        # "medium": str(obj.utm_medium).encode("ascii", "ignore").decode().strip(),
        # "campaign": str(obj.utm_campaign).encode("ascii", "ignore").decode().strip(),
        "cf_payment_status": "Complete",
        "cf_fee_waiver_category": "Free of cost (FOC)",
        "cf_institution_university": obj.university,
        # "cf_refferal_code":validate_data.get('referred_code'),
        # "cf_reference_code":refferals_code,
        # "cf_gcc_application_number":generate_application_id
    }
    # if obj.city:
    #     payload["city"] = obj.city
    # if obj.state:
    #     payload["state"] = obj.state
    # if obj.university:
    #     payload["cf_fee_waiver_category"] = obj.fee_waiver_category
    users = User.objects.filter(email=obj.email)
    if users:
        uu = users.first()
        clean_value = re.sub(r'[^A-Za-z0-9_]', '', uu.referred_code)
        print("clean values...",clean_value)
        payload["cf_refferal_code"] = clean_value
        payload["cf_reference_code"] = uu.referral_code
        payload["cf_gcc_application_number"] = uu.application_id
    print("merito data.......",payload)

    try:
        response = requests.post(url, headers=headers, json=payload)
        print(response.status_code)
        print(response.text)
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Meritto API Error:", str(e))
        return None


class CreateOrUpdateDossierDataMerittoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierData
        fields = "__all__"

    def create(self, validated_data):
        instance = super().create(validated_data)
        push_to_meritto(instance)
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        push_to_meritto(instance)
        return instance

    
import threading
from gcc_backend.utils import create_affliate_seven_services_async

class CreateDossierDataCustomAffliateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierData
        # fields = ["full_name","email","phone","city","state","source"]
        fields = "__all__"

    def create(self, validated_data):
        validated_data["fee_waiver_category"] = "Free of cost (FOC)"
        instance = super().create(validated_data)
        src_type = instance.source

        threading.Thread(
                    target=create_affliate_seven_services_async,
                    args=(instance, src_type),
                    daemon=True,
                ).start()

        print("complete response")
        # if settings.MERITO_STATUS == "True":
        #     if src_type == 15:
        #         m_source = "gccaffiliateSeven"
        #     else:
        #         m_source = "gcc"
        #     # API URL
        #     url = settings.MERITO_BASE_URL+"/lead/v1/createOrUpdate"

        #     headers = {
        #         "Content-Type": "application/json",
        #         "secret-key": settings.MERITO_SECRETE_KEY,
        #         "access-key": settings.MERITO_ACCESS_KEY
        #     }

        #     payload = {
        #         "name": instance.full_name,
        #         "email": instance.email,
        #         "mobile": instance.phone,
        #         "city": instance.city,
        #         "state": instance.state,
        #         "search_criteria": "email",
        #         "source":m_source,
        #         "cf_source":m_source,
        #         "cf_payment_status":"Complete",
        #         "cf_fee_waiver_category":"Free of cost (FOC)"
        #     }
        #     try:
        #         print("mer..",payload)
        #         response = requests.post(url, headers=headers, json=payload)
        #         print(response.status_code)
        #         print(response.text)
        #         DossierLog.objects.create(dossier=instance, message=response.text, status=int(response.status_code), activity="creating", datas=validated_data)
        #     except Exception as e:
        #         print("API Error:", str(e))

        # if settings.EXCEL_INPUT == "True":
        #     if src_type == 15:
        #         print("sheet enter")
        #         if not DossierData.objects.filter(phone=instance.phone, source=src_type).exclude(id=instance.id).exists():
        #             print("valida data")
        #             try:
        #                 sheet = get_google_sheet_affliate_seven()
        #                 print("open sheet...",sheet)
        #                 local_time = timezone.localtime(instance.created_at)
        #                 create_times = local_time.strftime("%Y-%m-%d %H:%M:%S")
        #                 row = [
        #                     instance.full_name,
        #                     instance.email,
        #                     instance.phone,
        #                     instance.city,
        #                     instance.state,
        #                     instance.degree,
        #                     instance.age_range,
        #                     instance.degree_stage,
        #                     instance.fund_mode,
        #                     instance.attend_from,
        #                     "No",
        #                     "",
        #                     create_times
        #                 ]
        #                 print("data inster",row)
        #                 sheet.append_row(row)
        #                 print("completed")
        #             except Exception as e:
        #                 print("google sheet error", str(e))



        # url = settings.CSRF_TRUSTED_ORIGINS[0]+"/api/users/create_student/"

        # payload = {
        #     "full_name": instance.full_name,
        #     "email": instance.email,
        #     "phone1": instance.phone
        # }
        # try:
        #     print("user....",payload)
        #     response = requests.post(url, json=payload)
        #     print(response.status_code)
        #     print(response.text)
        #     User.objects.filter(email=instance.email).update(city=instance.city, state=instance.state, fee_waiver_category="Free of cost (FOC)")
        #     # DossierLog.objects.create(dossier=instance, message=response.text, status=int(response.status_code), activity="creating", datas=validated_data)
        # except Exception as e:
        #     print("API Error:", str(e))    

        return instance


class ListDossierDataAffliateSevenInterviewSerializer(serializers.ModelSerializer):
    # created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    created_at = serializers.SerializerMethodField()
    # interview_booked_status = serializers.SerializerMethodField('get_interview_booked_status')
    class Meta:
        model = DossierData
        fields = ["full_name","email","phone","created_at","interview_date"]
        
    def get_created_at(self, obj):
        if obj.created_at:
            local_time = timezone.localtime(obj.created_at)
            return local_time.strftime("%Y-%m-%d %H:%M:%S")
        return None

class ListDossierDataAffliateSevenInterviewLiveReportSerializer(serializers.ModelSerializer):
    # created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    created_at = serializers.SerializerMethodField()
    interview_booked_status = serializers.SerializerMethodField('get_interview_booked_status')
    interview_date = serializers.SerializerMethodField('get_interview_date')
    class Meta:
        model = DossierData
        fields = ["full_name","email","phone","city","state","created_at","interview_date","interview_booked_status"]
        
    def get_created_at(self, obj):
        if obj.created_at:
            local_time = timezone.localtime(obj.created_at)
            return local_time.strftime("%Y-%m-%d %H:%M:%S")
        return None
    def get_interview_booked_status(self, obj):
        if not obj.interview_date:
            ans = "No"
            std = StudentProfile.objects.filter(email=obj.email)
            if std:
                dd = std.last()
                intr = ManageStudentInterview.objects.filter(profile=dd)
                if intr:
                    ans = "Yes"
            return ans
        return "Yes"
    
    def get_interview_date(self, obj):
        print("datas..",obj.interview_date)
        print("numm.....",obj.id)
        if not obj.interview_date:
            dds = ""
            std = StudentProfile.objects.filter(email=obj.email)
            if std:
                dd = std.last()
                intr = ManageStudentInterview.objects.filter(profile=dd)
                if intr:
                    data = intr.last()
                    dds = data.interview_date
            return dds
        return obj.interview_date.strftime("%Y-%m-%d")