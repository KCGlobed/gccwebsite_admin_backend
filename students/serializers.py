from rest_framework import serializers
from .models import *
from career.models import DossierData
from career.serializers import ListDossierDataSerializer
from django.utils import timezone

class ListStudentQuerySerializer(serializers.ModelSerializer) :
    class Meta:
        model = StudentEnquiries
        fields = "__all__"


class ListStudentDataSerializer(serializers.ModelSerializer) :
    class Meta:
        model = StudentsData
        fields = "__all__"


class ListStudentPaymentSerializer(serializers.ModelSerializer) :
    class Meta:
        model = Payments
        fields = "__all__"
        depth=1



class ListDossierDataReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierData
        exclude = ["created_at","updated_at"]



class ListPaymentPDFSerializer(serializers.ModelSerializer) :
    created_at = serializers.SerializerMethodField('get_created_at')
    class Meta:
        model = Payments
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Fetch related form
        form_obj = DossierData.objects.filter(id=instance.form_id).first()

        if form_obj:
            form_data = ListDossierDataReportSerializer(form_obj).data
            # Merge form fields into main response
            data.update(form_data)

        return data
    
    def get_created_at(self, obj):
        if obj.created_at:
            # Convert to project TIME_ZONE automatically
            local_dt = timezone.localtime(obj.created_at)

            formatted_date = local_dt.strftime("%B %d, %Y, %I:%M %p")

            # Remove leading zero and convert AM/PM to a.m./p.m.
            formatted_date = formatted_date.replace(" 0", " ")
            formatted_date = formatted_date.replace("AM", "a.m.").replace("PM", "p.m.")
        else:
            formatted_date = "--"
        return formatted_date



class ListPaymentExcelReportSerializer(serializers.ModelSerializer) :
    created_at = serializers.SerializerMethodField('get_created_at')
    class Meta:
        model = Payments
        fields = ["razorpay_order_id","razorpay_payment_id","amount","status","created_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Fetch related form
        form_obj = DossierData.objects.filter(id=instance.form_id).first()

        if form_obj:
            form_data = ListDossierDataReportSerializer(form_obj).data
            form_data.pop('id')
            # Merge form fields into main response
            data.update(form_data)

        return data
    
    def get_created_at(self, obj):
        if obj.created_at:
            # Convert to project TIME_ZONE automatically
            local_dt = timezone.localtime(obj.created_at)

            formatted_date = local_dt.strftime("%B %d, %Y, %I:%M %p")

            # Remove leading zero and convert AM/PM to a.m./p.m.
            formatted_date = formatted_date.replace(" 0", " ")
            formatted_date = formatted_date.replace("AM", "a.m.").replace("PM", "p.m.")
        else:
            formatted_date = "--"
        return formatted_date






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
