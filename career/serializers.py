from rest_framework import serializers
from .models import *
from django.conf import settings
from users.models import User
from users.serializers import StudentProfileDetailSerializer
import requests

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
        fields = ["full_name","email","phone","city","state","source","source_form"]
        
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
                "lead_stage": "hot",
                "search_criteria": "email",
                "city": instance.city,
                "state": instance.state,
                "country": "India",
                "source":m_source
            }

            try:
                response = requests.post(url, headers=headers, json=payload)
                print(response.status_code)
                print(response.text)
            except Exception as e:
                print("API Error:", str(e))
        
        return instance



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
                "name": vsl_obj.full_name,
                "email": vsl_obj.email,
                "mobile": vsl_obj.phone,
                "lead_stage": "hot",
                "search_criteria": "email",
                # "city": instance.city,
                # "state": instance.state,
                # "country": "India",
                "source":m_source
            }

            try:
                response = requests.post(url, headers=headers, json=payload)
                print(response.status_code)
                print(response.text)
            except Exception as e:
                print("API Error:", str(e))
        
        return vsl_obj



class CreateVslFinalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierData
        fields = ["full_name","email","phone","city","state"]
        
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
                "lead_stage": "hot",
                "search_criteria": "email",
                "city": vsl_obj.city,
                "state": vsl_obj.state,
                "country": "India",
                "source":m_source
            }

            try:
                response = requests.post(url, headers=headers, json=payload)
                print(response.status_code)
                print(response.text)
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








class ListDossierDataSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = DossierData
        fields = "__all__"
        

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
        


