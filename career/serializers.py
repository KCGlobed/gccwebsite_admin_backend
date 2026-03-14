from rest_framework import serializers
from .models import *
from django.conf import settings



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


from users.models import User
from users.serializers import StudentProfileDetailSerializer

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
        


