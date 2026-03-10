from rest_framework import serializers
from .models import *
from django.conf import settings



class ListCareerApplicationSerializer(serializers.ModelSerializer) :
    resume_path = serializers.SerializerMethodField('get_resume_path')
    class Meta:
        model = CareerApplication
        fields = "__all__"
    
    def get_resume_path(self, obj):
        url = f'https://storage.googleapis.com/{settings.GS_BUCKET_NAME}/{obj.resume_path}'
        return url

class ListPartnerWithUsSerializer(serializers.ModelSerializer) :
    class Meta:
        model = PartnerWithUs
        fields = "__all__"
        


class ListDossierDataSerializer(serializers.ModelSerializer) :
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = DossierData
        fields = "__all__"
        

class ListNewsletterSubscriberSerializer(serializers.ModelSerializer) :
    class Meta:
        model = NewsletterSubscribers
        fields = "__all__"
        


