from rest_framework import serializers
from .models import *
from users.models import *
from career.models import DossierData
from career.serializers import ListDossierDataSerializer
from django.utils import timezone
import json
from datetime import datetime, timedelta, date
import requests
from django.conf import settings


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
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d")

    class Meta:
        model = CampusFaculty
        fields = "__all__"


class ListCampusFacultyPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusFaculty
        fields = "__all__"


class ListCampusStudentSerializer(serializers.ModelSerializer) :
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d")
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


class ContactUsSerializer(serializers.ModelSerializer) :
    first_name = serializers.CharField(max_length = 255, required=True)
    last_name = serializers.CharField(max_length = 255, required=True)
    email = serializers.CharField(max_length = 255, required=True)
    phone = serializers.CharField(max_length = 255, required=True)
    state = serializers.CharField(max_length = 255, required=True)
    city = serializers.CharField(max_length = 255, required=True)
    class Meta:
        model = ContactUs
        fields = ['first_name','last_name','email','phone',"state","city"]
        
    def validate(self, data):

        return data


    def create(self , validate_data):
        
        query = ContactUs(
            first_name = validate_data.get('first_name'),
            last_name = validate_data.get('last_name'),
            email = validate_data.get('email'),
            phone = validate_data.get('phone'),
            state = validate_data.get('state'),
            city = validate_data.get('city'),

        )
        query.save()
        
        return query
    

class ContactListSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d")
    
    class Meta:
        model = ContactUs
        fields = ['id',"first_name","last_name",'email',"phone","state","city","message","created_at"]


class ExperienceSerializer(serializers.Serializer):
    company_name = serializers.CharField(required=False, allow_blank=True)
    position = serializers.CharField(required=False, allow_blank=True)
    area = serializers.CharField(required=False, allow_blank=True)
    start_date = serializers.DateField(required=False, allow_null = True)
    end_date = serializers.DateField(required=False, allow_null = True)

class CompleteStudentSerializer(serializers.ModelSerializer) :
    user = serializers.IntegerField(required=True)
    first_name = serializers.CharField(max_length = 255, required=True)
    last_name = serializers.CharField(max_length = 255, required=True)
    email = serializers.CharField(max_length = 255, required=True)
    phone = serializers.CharField(max_length = 255, required=True)
    state = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    contact_name = serializers.CharField(required=False, allow_blank=True)
    contact_phone = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null = True)
    gender = serializers.IntegerField(required=True)
    nationality = serializers.CharField(required=False, allow_blank=True)
    pincode = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    tenth_passing_year = serializers.IntegerField(required=False, allow_null = True)
    tenth_passing_percentage = serializers.FloatField(required=False, allow_null = True)
    tenth_score_type = serializers.CharField(required=False, allow_null = True)
    tenth_medium = serializers.IntegerField(required=False, allow_null = True)
    twelveth_passing_year = serializers.IntegerField(required=False, allow_null = True)
    twelveth_passing_percentage = serializers.FloatField(required=False, allow_null = True)
    twelveth_score_type = serializers.CharField(required=False, allow_null = True)
    twelveth_medium = serializers.IntegerField(required=False, allow_null = True)
    medium_instruction = serializers.IntegerField(required=False)
    other_instruction = serializers.CharField(required=False, allow_blank=True)
    pg_status = serializers.IntegerField(required=False)
    pg_percentage = serializers.FloatField(required=False, allow_null = True)
    ug_score_type = serializers.CharField(required=False, allow_null = True)
    institution = serializers.CharField(required=False, allow_blank=True)
    higher_education_status = serializers.IntegerField(required=False)
    higher_qualification = serializers.CharField(required=False, allow_blank=True)
    higher_qualification_institution = serializers.CharField(required=False, allow_blank=True)
    employement_status = serializers.IntegerField(required=False)
    higher_qualification_institution = serializers.CharField(required=False, allow_blank=True)
    aadhaar = serializers.FileField(required=False,allow_null=True)
    dob_certificate = serializers.FileField(required=False,allow_null=True)
    photo = serializers.FileField(required=False,allow_null=True)
    signature = serializers.FileField(required=False,allow_null=True)
    user_experience = serializers.JSONField()
    

    class Meta:
        model = StudentProfile
        fields = ["user",'first_name','last_name','email','phone',"state","city","contact_name","contact_phone","date_of_birth","gender","nationality","pincode","address","tenth_passing_year","tenth_passing_percentage","tenth_score_type","tenth_medium","twelveth_passing_year","twelveth_passing_percentage","twelveth_score_type","twelveth_medium","medium_instruction","other_instruction","pg_status","pg_percentage","ug_score_type","institution","higher_education_status","higher_qualification","higher_qualification_institution","employement_status","aadhaar","dob_certificate","photo","signature","user_experience"]
        
    def validate(self, data):
        return data
    
    def validate_user_experience(self, value):
        # 1. Convert string to Python list if necessary
        
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Malformed JSON string.")

        # 2. Run the data through a nested serializer for strict validation
        serializer = ExperienceSerializer(data=value, many=True)
        if serializer.is_valid():
            return serializer.validated_data
        raise serializers.ValidationError(serializer.errors)


    def create(self , validate_data):
        
        datas = StudentProfile.objects.filter(user_id = validate_data.get('user')).first()
        print(validate_data.get('user_experience'))
        print(type(validate_data.get('user_experience')))
        if datas is not None:
            datas.first_name = validate_data.get('first_name', datas.first_name)
            datas.last_name = validate_data.get('last_name', datas.last_name)
            datas.email = validate_data.get('email', datas.email)
            datas.phone = validate_data.get('phone', datas.phone)
            datas.state = validate_data.get('state', datas.state)
            datas.city = validate_data.get('city', datas.city)
            datas.contact_name = validate_data.get('contact_name',datas.contact_name)
            datas.contact_phone = validate_data.get('contact_phone', datas.contact_phone)
            datas.date_of_birth = validate_data.get('date_of_birth', datas.date_of_birth)
            datas.gender = validate_data.get('gender', datas.gender)
            datas.nationality = validate_data.get('nationality', datas.nationality)
            datas.pincode = validate_data.get('pincode', datas.pincode)
            datas.address = validate_data.get('address', datas.address)
            datas.tenth_passing_year = validate_data.get('tenth_passing_year', datas.tenth_passing_year)
            datas.tenth_passing_percentage = validate_data.get('tenth_passing_percentage', datas.tenth_passing_percentage)
            datas.tenth_score_type = validate_data.get('tenth_score_type', datas.tenth_score_type)
            datas.tenth_medium = validate_data.get('tenth_medium', datas.tenth_medium)
            datas.twelveth_passing_year = validate_data.get('twelveth_passing_year', datas.twelveth_passing_year)
            datas.twelveth_passing_percentage = validate_data.get('twelveth_passing_percentage', datas.twelveth_passing_percentage)
            datas.twelveth_score_type = validate_data.get('twelveth_score_type', datas.twelveth_score_type)
            datas.twelveth_medium = validate_data.get('twelveth_medium', datas.twelveth_medium)
            datas.medium_instruction = validate_data.get('medium_instruction', datas.medium_instruction)
            datas.other_instruction = validate_data.get('other_instruction', datas.other_instruction)
            datas.pg_status = validate_data.get('pg_status', datas.pg_status)
            datas.pg_percentage = validate_data.get('pg_percentage', datas.pg_percentage)
            datas.ug_score_type = validate_data.get('ug_score_type', datas.ug_score_type)
            datas.institution = validate_data.get('institution', datas.institution)
            datas.higher_education_status = validate_data.get('higher_education_status', datas.higher_education_status)
            datas.higher_qualification = validate_data.get('higher_qualification', datas.higher_qualification)
            datas.higher_qualification_institution = validate_data.get('higher_qualification_institution', datas.higher_qualification_institution)
            datas.employement_status = validate_data.get('employement_status', datas.employement_status)
            datas.aadhaar = validate_data.get('aadhaar', datas.aadhaar)
            datas.dob_certificate = validate_data.get('dob_certificate', datas.dob_certificate)
            datas.photo = validate_data.get('photo', datas.photo)
            datas.signature = validate_data.get('signature', datas.signature)
            datas.save()
            query = datas
            if len(validate_data.get('user_experience')) > 0:
                StudentExperience.objects.filter(student_profile = query).delete()
                for exp in validate_data.get('user_experience'):
                    experience = StudentExperience(
                        student_profile = query,
                        position = exp.get('position'),
                        company_name = exp.get('company_name'),
                        area = exp.get('area'),
                        start_date = exp.get('start_date'),
                        end_date = exp.get('end_date'),

                    )
                    experience.save()

        else:
            query = StudentProfile(
                user = User.objects.filter(id = validate_data.get('user')).first(),
                last_name = validate_data.get('last_name'),
                first_name = validate_data.get('first_name'),
                email = validate_data.get('email'),
                phone = validate_data.get('phone'),
                state = validate_data.get('state'),
                city = validate_data.get('city'),
                contact_name = validate_data.get('contact_name'),
                contact_phone = validate_data.get('contact_phone'),
                date_of_birth = validate_data.get('date_of_birth'),
                gender = validate_data.get('gender'),
                nationality = validate_data.get('nationality'),
                pincode = validate_data.get('pincode'),
                address = validate_data.get('address'),
                tenth_passing_year = validate_data.get('tenth_passing_year'),
                tenth_passing_percentage = validate_data.get('tenth_passing_percentage'),
                tenth_score_type = validate_data.get('tenth_score_type'),
                tenth_medium = validate_data.get('tenth_medium'),
                twelveth_passing_year = validate_data.get('twelveth_passing_year'),
                twelveth_passing_percentage = validate_data.get('twelveth_passing_percentage'),
                twelveth_score_type = validate_data.get('twelveth_score_type'),
                twelveth_medium = validate_data.get('twelveth_medium'),
                medium_instruction = validate_data.get('medium_instruction'),
                other_instruction = validate_data.get('other_instruction'),
                pg_status = validate_data.get('pg_status'),
                pg_percentage = validate_data.get('pg_percentage'),
                ug_score_type = validate_data.get('ug_score_type'),
                institution = validate_data.get('institution'),
                higher_education_status = validate_data.get('higher_education_status'),
                higher_qualification = validate_data.get('higher_qualification'),
                higher_qualification_institution = validate_data.get('higher_qualification_institution'),
                employement_status = validate_data.get('employement_status'),
                aadhaar = validate_data.get('aadhaar'),
                dob_certificate = validate_data.get('dob_certificate'),
                photo = validate_data.get('photo'),
                signature = validate_data.get('signature')

            )
            query.save()

            if len(validate_data.get('user_experience')) > 0:
                for exp in validate_data.get('user_experience'):
                    experience = StudentExperience(
                        student_profile = query,
                        position = exp.get('position'),
                        company_name = exp.get('company_name'),
                        area = exp.get('area'),
                        start_date = exp.get('start_date'),
                        end_date = exp.get('end_date'),

                    )
                    experience.save()
            
        return query
    


class StudentSlotBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ["slot_date", "slot_time"]
    
    def update(self, instance, validated_data):
        if instance.slot_update_count >= 2:
            raise serializers.ValidationError(
                {
                    "status": 400,
                    "message": "This slot has already been updated once and cannot be changed again.",
                    "data":[]
                }
            )
        
        instance.slot_date = validated_data.get("slot_date", instance.slot_date)
        instance.slot_time = validated_data.get("slot_time", instance.slot_time)

        instance.slot_update_count += 1
        instance.save()

        return instance


class StudentExperienceRelationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = StudentExperience
        fields = "__all__"


class StudentProfileSerializer(serializers.ModelSerializer):
    student_experience = serializers.SerializerMethodField()
    exam_status = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    application_id = serializers.SerializerMethodField("get_application_id")

    def get_student_experience(self, obj):
        answe = StudentExperience.objects.filter(student_profile_id =obj.id).order_by("id")
        return StudentExperienceRelationSerializer(answe, many=True).data
    
    def get_exam_status(self, obj):
        status=False
        if obj.slot_date:
            print(datetime.now().date())
            if obj.slot_date == datetime.now().date():
                start_str, end_str = obj.slot_time.split(" - ")
                current_time = datetime.now().time().replace(microsecond=0)
                target_time = datetime.strptime(start_str, "%I:%M %p").time()
                dt1 = datetime.combine(date.today(), current_time)
                dt2 = datetime.combine(date.today(), target_time)

                diff = abs((dt1 - dt2).total_seconds())
                print(diff)
                if diff <= 3600:   # 3600 seconds = 1 hour
                    status=True
        return status
    
    def get_application_id(self, obj):
        app_id = "--"
        if obj.user:
            app_id = obj.user.application_id
        return app_id

    class Meta:
        model = StudentProfile
        fields = "__all__"




class StudentMockTestCompleteStatusSerializer(serializers.ModelSerializer):
    email  = serializers.EmailField(required=True)
    status = serializers.BooleanField(required=True)

    class Meta:
        model = StudentProfile
        fields = ["email","status"]
    
    def update(self, instance, validated_data):
        if validated_data.get("status") != True:
            raise serializers.ValidationError(
                {
                    "status": 400,
                    "message": "Please Select Valid Status.",
                    "data":[]
                }
            )
        instance.mock_test_status = 2 if validated_data.get("status") == True else 1
        instance.save()

        return instance

class StudentMockTestStartStatusSerializer(serializers.ModelSerializer):
    email  = serializers.EmailField(required=True)
    status = serializers.BooleanField(required=True)

    class Meta:
        model = StudentProfile
        fields = ["email","status"]
    
    def update(self, instance, validated_data):
        if validated_data.get("status") != True:
            raise serializers.ValidationError(
                {
                    "status": 400,
                    "message": "Please Select Valid Status.",
                    "data":[]
                }
            )
        instance.mock_test_status = 1 if validated_data.get("status") == True else 0
        instance.save()

        return instance




class CampusStudentAccountEmailStatusSerializer(serializers.ModelSerializer):
    status = serializers.BooleanField(required=True)

    class Meta:
        model = CampusStudent
        fields = ["status"]

    def update(self, instance, validated_data):

        if validated_data.get("status") is not True:
            raise serializers.ValidationError({
                "status": 400,
                "message": "Please Select Valid Status.",
                "data": {}
            })
        if instance.is_verified is not True:
            raise serializers.ValidationError({
                "status": 400,
                "message": "Account is not verified yet.",
                "data": {}
            })

        url = settings.CSRF_TRUSTED_ORIGINS[0] + "/api/users/create_student/"

        payload = {
            "full_name": instance.full_name,
            "email": instance.email,
            "phone1": instance.mobile,
            "city": instance.city,
            "state": instance.state,
            "country": "India"
        }

        try:
            response = requests.post(url, json=payload, timeout=5)

            data = response.json()

            if response.status_code != 200:
                raise serializers.ValidationError({
                    "status": 400,
                    "message": "Student creation API failed",
                    "data": data
                })

            if data.get("non_field_errors"):
                raise serializers.ValidationError({
                    "status": 400,
                    "message": data["non_field_errors"][0],
                    "data": {}
                })

        except requests.exceptions.RequestException as e:
            raise serializers.ValidationError({
                "status": 500,
                "message": f"External API Error: {str(e)}",
                "data": {}
            })
        
        instance.mail_status = True
        instance.save()

        return instance
    



class CampusStudentVerifiedStatusSerializer(serializers.ModelSerializer):
    status = serializers.BooleanField(required=True)
    remarks = serializers.CharField(required=True)

    class Meta:
        model = CampusStudent
        fields = ["status", "remarks"]

    def validate_status(self, value):
        if value is not True:
            raise serializers.ValidationError("Please select a valid status.")
        return value

    def validate_remarks(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("Remarks cannot be empty.")

        if len(value.strip()) < 10:
            raise serializers.ValidationError("Remarks must be at least 5 characters long.")

        return value.strip()

    def update(self, instance, validated_data):
        instance.is_verified = True
        instance.remarks = validated_data.get("remarks")
        instance.save()
        return instance


