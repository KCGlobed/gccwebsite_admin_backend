from rest_framework import serializers
from .models import *



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


class ListCampusFacultySerializer(serializers.ModelSerializer) :
    class Meta:
        model = CampusFaculty
        fields = "__all__"


class ListCampusStudentSerializer(serializers.ModelSerializer) :
    class Meta:
        model = CampusStudent
        fields = "__all__"
        

class CampusStudentPDFSerializer(serializers.ModelSerializer):

    # full_name = serializers.SerializerMethodField()
    # student_body_member = serializers.SerializerMethodField()
    # consent = serializers.SerializerMethodField()

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

    # -------- Null-safe fields -------- #

    # def get_full_name(self, obj):
    #     return f"{obj.first_name or ''} {obj.last_name or ''}".strip() or "—"

    # def get_student_body_member(self, obj):
    #     return "Yes" if obj.student_body_member else "No"

    # def get_consent(self, obj):
    #     return "Yes" if obj.consent else "No"

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Replace all None / empty with —
        for k, v in data.items():
            if v in [None, "", []]:
                data[k] = "—"

        return data