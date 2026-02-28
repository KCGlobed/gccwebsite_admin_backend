from rest_framework import serializers
from .models import *
from career.models import DossierData
from career.serializers import ListDossierDataSerializer


class ListStudentQuerySerializer(serializers.ModelSerializer) :
    class Meta:
        model = StudentEnquiries
        fields = "__all__"


class ListStudentDataSerializer(serializers.ModelSerializer) :
    class Meta:
        model = StudentsData
        fields = "__all__"


class ListStudentPaymentSerializer(serializers.ModelSerializer) :
    forms_detail = serializers.SerializerMethodField('get_forms_detail')
    class Meta:
        model = Payments
        fields = "__all__"

    def get_forms_detail(self, obj):
        if obj.form_type == 1:
            forms_data = []
        if obj.form_type == 2:
            forms_obj = DossierData.objects.filter(id=obj.form_id)
            forms_data = ListDossierDataSerializer(forms_obj, many=True).data
        else:
            forms_data = []

        return forms_data



class ListPaymentExcelReportSerializer(serializers.ModelSerializer) :
    class Meta:
        model = Payments
        fields = ["razorpay_order_id","razorpay_payment_id","amount","status"]




class ListCampusFacultySerializer(serializers.ModelSerializer) :
    class Meta:
        model = CampusFaculty
        fields = "__all__"


class ListCampusStudentSerializer(serializers.ModelSerializer) :
    class Meta:
        model = CampusStudent
        fields = "__all__"
        

class CampusStudentPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusStudent
        fields = [
            "full_name",
            "email",
            "mobile",
            "city",
            "state",
            "address",
            "college_name",
            "program_of_study",
            "program_other",
            "semester",
            "student_body_member",
            "campus_ambassador_history",
            "inspiration",
            "student_reach",
            "consent",
        ]


    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Replace all None / empty with —
        for k, v in data.items():
            if v in [None, "", []]:
                data[k] = "—"

        return data




class CampusStudentExcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusStudent
        fields = [
            "full_name",
            "email",
            "mobile",
            "city",
            "state",
            "address",
            "college_name",
            "program_of_study",
            "program_other",
            "semester",
            "student_body_member",
            "campus_ambassador_history",
            "inspiration",
            "student_reach"
        ]
