from rest_framework import serializers
from .models import *




class ListCareerApplicationSerializer(serializers.ModelSerializer) :
    class Meta:
        model = CareerApplication
        fields = "__all__"


class ListPartnerWithUsSerializer(serializers.ModelSerializer) :
    class Meta:
        model = PartnerWithUs
        fields = "__all__"
        


class ListDossierDataSerializer(serializers.ModelSerializer) :
    class Meta:
        model = DossierData
        fields = "__all__"
        


