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
            "country": "India"
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            print(response.status_code)
            print(response.text)
        except Exception as e:
            print("API Error:", str(e))
        
        return instance



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
        


