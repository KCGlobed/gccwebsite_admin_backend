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
        exclude = ["created_at","updated_at","fee_waiver_category"]



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
        fields = ["razorpay_order_id","razorpay_payment_id","amount","status","created_at","fee_waiver_category"]

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




class ListStudentProfileExcelReportSerializer(serializers.ModelSerializer) :
    created_at = serializers.SerializerMethodField('get_created_at')
    tenth_medium = serializers.SerializerMethodField('get_tenth_medium')
    twelveth_medium = serializers.SerializerMethodField('get_twelveth_medium')
    gender = serializers.SerializerMethodField('get_gender')
    employement_status = serializers.SerializerMethodField('get_employement_status')
    higher_education_status = serializers.SerializerMethodField('get_higher_education_status')
    pg_status = serializers.SerializerMethodField('get_pg_status')
    medium_instruction = serializers.SerializerMethodField('get_medium_instruction')
    referral_code = serializers.SerializerMethodField("get_referral_code")
    referred_code = serializers.SerializerMethodField("get_referred_code")
    student_result = serializers.SerializerMethodField("get_student_result")
    guardian_dropdown = serializers.SerializerMethodField("get_guardian_dropdown")
    
    class Meta:
        model = StudentProfile
        fields = "__all__"

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)

    #     return data

    def get_referral_code(self, obj):
        name = obj.user.referral_code if obj.user else ""
        return name

    def get_referred_code(self, obj):
        name = obj.user.referred_code if obj.user else ""
        return name
     
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
    
    def get_tenth_medium(self, obj):
        return obj.get_tenth_medium_display()
    def get_twelveth_medium(self, obj):
        return obj.get_twelveth_medium_display()
    def get_medium_instruction(self, obj):
        return obj.get_medium_instruction_display()
    def get_gender(self, obj):
        return obj.get_gender_display()
    def get_pg_status(self, obj):
        return obj.get_pg_status_display()
    def get_employement_status(self, obj):
        name = "N/A"
        if str(obj.employement_status) == "1":
            name = "Fresher"
        else:
            name = "Experience"
        return name
    def get_higher_education_status(self, obj):
        name = "N/A"
        if str(obj.higher_education_status) == "1":
            name = "YES"
        else:
            name = "No"
        return name
    def get_student_result(self, obj):

        total_score = ""
        std_result  = StudentRealExamResult.objects.filter(student_profile=obj.id)
        if std_result:
            result      = std_result.last()
            total_score = str(round((float(result.totalscore) / float(result.totalquestions)) * 100, 2))

        return total_score

    def get_guardian_dropdown(self, obj):
        return obj.get_guardian_dropdown_display()



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
        print(validate_data)
        user_obj = User.objects.filter(id = validate_data.get('user')).first()
        datas = StudentProfile.objects.filter(user_id = validate_data.get('user')).first()
        exp_payload = {"have_work_ex":"Fresher (Currently Studying or Recently Graduated)"}
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
            datas.application_id = user_obj.application_id
            datas.fee_waiver_category = user_obj.fee_waiver_category
            datas.save()
            query = datas
            if len(validate_data.get('user_experience')) > 0:
                num = 1
                exp_payload["have_work_ex"] = "Experienced (Currently Working or Have Past Experience)"
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

                    key1 = f"field_334047_{num}_1"
                    value1 = exp.get('company_name')
                    key2 = f"field_334047_{num}_2"
                    value2 = exp.get('position')
                    key3 = f"field_334047_{num}_3"
                    value3 = exp.get('area')
                    key4 = f"field_334047_{num}_4"
                    value4 = exp.get('start_date').strftime("%d/%m/%Y")
                    key5 = f"field_334047_{num}_5"
                    print("experience.end_date....",experience.end_date)
                    value5 = exp.get('end_date').strftime("%d/%m/%Y") if experience.end_date else exp.get('start_date').strftime("%d/%m/%Y")
                    key6 = f"field_334047_{num}_6"
                    value6 = ""
                    print("values5...",value5)
                    exp_payload[key1] = value1
                    exp_payload[key2] = value2
                    exp_payload[key3] = value3
                    exp_payload[key4] = value4
                    exp_payload[key5] = value5
                    exp_payload[key6] = value6
                    print(exp_payload)
                    num+=1

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
                signature = validate_data.get('signature'),
                application_id = user_obj.application_id,
                fee_waiver_category = user_obj.fee_waiver_category
            )
            query.save()
            print(validate_data)
            if len(validate_data.get('user_experience')) > 0:
                num = 1
                exp_payload["have_work_ex"] = "Experienced (Currently Working or Have Past Experience)"
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

                    key1 = f"field_334047_{num}_1"
                    value1 = exp.get('company_name')
                    key2 = f"field_334047_{num}_2"
                    value2 = exp.get('position')
                    key3 = f"field_334047_{num}_3"
                    value3 = exp.get('area')
                    key4 = f"field_334047_{num}_4"
                    value4 = exp.get('start_date').strftime("%d/%m/%Y")
                    key5 = f"field_334047_{num}_5"
                    print("experience.end_date....",experience.end_date)
                    value5 = exp.get('end_date').strftime("%d/%m/%Y") if experience.end_date else exp.get('start_date').strftime("%d/%m/%Y")
                    key6 = f"field_334047_{num}_6"
                    value6 = ""

                    print("values5...",value5)

                    exp_payload[key1] = value1
                    exp_payload[key2] = value2
                    exp_payload[key3] = value3
                    exp_payload[key4] = value4
                    exp_payload[key5] = value5
                    exp_payload[key6] = value6

                    print(exp_payload)
                    
                    num+=1

        if settings.MERITO_STATUS == "True":
            if int(query.gender) == 1:
                mgender = "Male"
            elif int(query.gender) == 2:
                mgender = "Female"
            else:
                mgender = "Other"

            if int(query.tenth_medium) == 1:
                mtmedium = "English"
            elif int(query.tenth_medium) == 2:
                mtmedium = "Hindi"
            else:
                mtmedium = "Other"

            if int(query.twelveth_medium) == 1:
                mthmedium = "English"
            elif int(query.twelveth_medium) == 2:
                mthmedium = "Hindi"
            else:
                mthmedium = "Other"

            if int(query.medium_instruction) == 1:
                minstrmedium = "English"
            elif int(query.medium_instruction) == 2:
                minstrmedium = "Hindi"
            else:
                minstrmedium = "Other"

            if query.higher_education_status == 1:
                higher_status = "Yes"
            else:
                higher_status = "No"

            if query.pg_status == 1:
                pg_status = "Completed"
            else:
                pg_status = "Pursuing"


            tenth_score_type = query.tenth_score_type if query.tenth_score_type == "Percentage" else "CGPA out of 10"
            twelveth_score_type = query.twelveth_score_type if query.twelveth_score_type == "Percentage" else "CGPA out of 10"

            meritto_payload = {
                "form_id": 22144,
                "email": query.email,
                "search_criteria":"email",
                "data": {
                        "first_name":query.first_name,
                        "last_name":query.last_name,
                        "email":query.email,
                        "mobile_no":f"+91-{query.phone}",
                        "father_first_name":"",
                        "father_mobile_no":"",
                        "date_of_birth":query.date_of_birth.strftime("%d/%m/%Y"),
                        "gender":mgender,
                        "nationality":"Indian",
                        "field_339552":query.state,
                        "field_339553":query.city,
                        "field_337926":query.pincode,
                        "field_340085":query.address,
                        # "field_340065":query.contact_name,
                        "field_340066":f"+91-{query.contact_phone}",
                        "field_333993_1_1":query.tenth_passing_year,
                        "field_333993_1_2":tenth_score_type,
                        "field_333993_1_3":query.tenth_passing_percentage,
                        "field_333993_1_4":mtmedium,
                        "field_333994_1_1":query.twelveth_passing_year,
                        "field_333994_1_2":twelveth_score_type,
                        "field_333994_1_3":query.twelveth_passing_percentage,
                        "field_333994_1_4":mthmedium,
                        "field_340097_1_1":query.institution,
                        "field_340097_1_2":query.ug_score_type,
                        "field_340097_1_3":query.pg_percentage,
                        "field_340097_1_4":query.pg_percentage,
                        "field_340069":pg_status,
                        "field_340077":higher_status,
                        "field_340079":query.higher_qualification_institution,
                        # "field_340078":query.higher_qualification,
                        "field_342113":query.user.application_id,
                        # "field_343097":"Complete",
                        "field_343098":"Complete"
                }
            }
            print(exp_payload)
            meritto_payload["data"].update(exp_payload) 
            leads = list(DossierData.objects.filter(email=query.email).values_list('id'))
            payment_obj = Payments.objects.filter(dossier_form__in=leads, status="success")
            if payment_obj:
                pay = payment_obj.first()
                payment_payload = {
                    "field_342107":pay.razorpay_signature,
                    "field_342105":pay.razorpay_order_id,
                    "field_342106":pay.razorpay_payment_id,
                    "field_342108":int(pay.amount),
                    "field_342111":"INR",
                    "field_342110":pay.created_at.strftime("%d/%m/%Y %I:%M:%S %p"),
                    "field_342109":"success"
                }
                meritto_payload["data"].update(payment_payload)

            
            print("meritto_payload...",meritto_payload)
            url = settings.MERITO_BASE_URL+"/application/v1/createOrUpdate"

            headers = {
                    "Content-Type": "application/json",
                    "secret-key": settings.MERITO_SECRETE_KEY,
                    "access-key": settings.MERITO_ACCESS_KEY
                }

            try:
                response = requests.post(url, headers=headers, json=meritto_payload)
                print(response.status_code)
                print(response.text)
            except Exception as e:
                print("API Error:", str(e))

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
        elif instance.slot_date and instance.slot_date <= datetime.now().date():
                start_str, end_str = instance.slot_time.split(" - ")
                current_time = datetime.now().time().replace(microsecond=0)
                target_time = datetime.strptime(start_str, "%I:%M %p").time()
                dt1 = datetime.combine(date.today(), current_time)
                dt2 = datetime.combine(date.today(), target_time)
                diff = abs((dt1 - dt2).total_seconds())
                if dt1>dt2:
                    raise serializers.ValidationError(
                        {
                            "status": 400,
                            "message": "No longer to change the slot.",
                            "data":[]
                        }
                    )

        instance.slot_date = validated_data.get("slot_date", instance.slot_date)
        instance.slot_time = validated_data.get("slot_time", instance.slot_time)

        instance.slot_update_count += 1
        instance.save()

        slot_count = StudentSlotBooking.objects.filter(student_profile=instance).count()
        std_booking = StudentSlotBooking(student_profile=instance, slot_date=validated_data.get("slot_date", instance.slot_date), slot_time=validated_data.get("slot_time", instance.slot_time), slot_count=slot_count)
        std_booking.save()
        

        if settings.MERITO_STATUS == "True":
            url = settings.MERITO_BASE_URL+"/application/v1/createOrUpdate"

            headers = {
                    "Content-Type": "application/json",
                    "secret-key": settings.MERITO_SECRETE_KEY,
                    "access-key": settings.MERITO_ACCESS_KEY
                }
            start_str, end_str = instance.slot_time.split(" - ")
            start_time = datetime.strptime(start_str, "%I:%M %p")
            # Format to HH:mm:ss
            start_formatted = start_time.strftime("%H:%M:%S %p")
            start_formatted_one = start_time.strftime("%H:%M:%S")
            print(f'''{instance.slot_date.strftime("%d/%m/%Y")} {start_formatted}''')
            meritto_payload = {
                "form_id": 22144,
                "email": instance.email,
                "search_criteria":"email",
                "data": {
                        # "field_342101":instance.slot_date.strftime("%d/%m/%Y"),
                        # "field_342102":start_formatted_one,
                        # "field_340093":instance.slot_date.strftime("%d/%m/%Y"),
                        "field_343386":f'''{instance.slot_date.strftime("%d/%m/%Y")} {start_formatted}''',
                        "field_343097": "Complete",
                        "field_343098":"Complete"
                        # "field_340094":instance.slot_time
                }
            }
            print(meritto_payload)
            try:
                response = requests.post(url, headers=headers, json=meritto_payload)
                print(response.status_code)
                print(response.text)
            except Exception as e:
                print("API Error:", str(e))

        return instance


class StudentExperienceRelationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = StudentExperience
        fields = "__all__"

class StudentReAttemptSerializer(serializers.ModelSerializer):
    status = serializers.BooleanField(required=True)
    class Meta:
        model = StudentProfile
        fields = ["status"]
    
    def update(self, instance, validated_data):
        if validated_data.get("status") != True:
            raise serializers.ValidationError(
                {
                    "status": 400,
                    "message": "Please Select Valid Status.",
                    "data":{}
                }
            )
        elif instance.re_attempt != 1 or instance.re_attempt_btn != 1 :
            raise serializers.ValidationError(
                {
                    "status": 400,
                    "message": "Invalid Request.",
                    "data":{}
                }
            )
        instance.re_attempt_btn = 2 if validated_data.get("status") == True else 1
        instance.slot_date = None
        instance.slot_time = ""
        instance.slot_update_count = 0
        instance.save()

        # pay_data = Payments.objects.filter()

        return instance
    
    class Meta:
        model = StudentProfile
        fields = ["status"]




class StudentProfileSerializer(serializers.ModelSerializer):
    student_experience = serializers.SerializerMethodField()
    exam_status = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    application_id = serializers.SerializerMethodField("get_application_id")
    student_result = serializers.SerializerMethodField("get_student_result")
    result_status = serializers.SerializerMethodField("get_result_status")
    referral_code = serializers.SerializerMethodField("get_referral_code")
    referred_code = serializers.SerializerMethodField("get_referred_code")
    exam_url = serializers.SerializerMethodField("get_exam_url")
    # guardian_dropdown = serializers.SerializerMethodField("get_guardian_dropdown")

    # def get_guardian_dropdown(self, obj):
    #     return obj.get_guardian_dropdown_display()

    def get_referral_code(self, obj):
        name = obj.user.referral_code if obj.user else ""
        return name

    def get_referred_code(self, obj):
        name = obj.user.referred_code if obj.user else ""
        return name

    def get_student_experience(self, obj):
        answe = StudentExperience.objects.filter(student_profile_id =obj.id).order_by("id")
        return StudentExperienceRelationSerializer(answe, many=True).data
    
    def get_result_status(self, obj):
        status = False
        std_result = StudentRealExamResult.objects.filter(student_profile=obj.id)
        if std_result:
            status = True
        return status
    
    def get_exam_status(self, obj):
        status=False
        if obj.slot_date:
            # print(datetime.now().date())
            if obj.slot_date == datetime.now().date():
                start_str, end_str = obj.slot_time.split(" - ")
                current_time = datetime.now().time().replace(microsecond=0)
                target_time = datetime.strptime(start_str, "%I:%M %p").time()
                dt1 = datetime.combine(date.today(), current_time)
                dt2 = datetime.combine(date.today(), target_time)

                diff = abs((dt1 - dt2).total_seconds())
                # print("diff time...",diff)
                # if diff <= 3600:   # 3600 seconds = 1 hour
                # if diff <= 120:   # 120 seconds = 2 min
                    # status=True
                # status=True
                # if obj.re_attempt == 1:
                #     status =  False

                status = True
                # if dt1>dt2:
                #     status = False
                if dt1<dt2:
                    status = False
                if dt1>dt2:
                    if diff >=5400:
                        obj.re_attempt = 1
                        obj.re_attempt_btn = 1
                        obj.save()
                        status = False
            elif obj.slot_date <= datetime.now().date():
                # print("datetime elif")
                start_str, end_str = obj.slot_time.split(" - ")
                current_time = datetime.now().time().replace(microsecond=0)
                target_time = datetime.strptime(start_str, "%I:%M %p").time()
                dt1 = datetime.combine(date.today(), current_time)
                dt2 = datetime.combine(date.today(), target_time)
                diff = abs((dt1 - dt2).total_seconds())
                if dt1>dt2:
                    if diff >=5400:
                        obj.re_attempt = 1
                        obj.re_attempt_btn = 1
                        obj.save()
        return status
    
    def get_application_id(self, obj):
        app_id = "--"
        if obj.user:
            app_id = obj.user.application_id
        return app_id
    
    def get_student_result(self, obj):

        total_score = ""
        std_result  = StudentRealExamResult.objects.filter(student_profile=obj.id)
        if std_result:
            result      = std_result.last()
            total_score = str(round((float(result.totalscore) / float(result.totalquestions)) * 100, 2))

        return total_score
    
    def get_exam_url(self, obj):

        exam_url = ""
        std_exam  = ManageMasterKey.objects.filter(profile=obj.id, status=False)
        if std_exam:
            result   = std_exam.first()
            exam_url = result.exam_url

        return exam_url
    
    
    class Meta:
        model = StudentProfile
        fields = "__all__"




class StudentMockTestCompleteStatusSerializer(serializers.ModelSerializer):
    email  = serializers.CharField(required=True)
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
            raise serializers.ValidationError("Remarks must be at least 10 characters long.")

        return value.strip()

    def update(self, instance, validated_data):
        instance.is_verified = True
        instance.remarks = validated_data.get("remarks")
        instance.save()
        return instance


class StudentCreatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        # fields = ["razorpay_order_id", "razorpay_payment_id","razorpay_signature","amount","currency","status","response","created_at","updated_at","form_type","form_id","dossier_form","source"]
        fields = "__all__"

    def create(self, validated_data):
        print("serializer payment request data..")
        print(validated_data)
        
        validated_data["response"] = json.loads(validated_data["response"])         
        validated_data["amount"] = float(validated_data["amount"])         
        validated_data["created_at"] = timezone.now()           
        validated_data["updated_at"] = timezone.now()   
        instance = super().create(validated_data)
        return instance

class PostExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentExamResult
        fields = "__all__"

    def create(self, validated_data):
        print("serializer request data..")
        print(validated_data)
        print("serializer end request data..")
        std_obj = StudentProfile.objects.filter(application_id=validated_data.get("email"))
        # if std_obj:
        #     validated_data["student_profile"] = std_obj.first()
        #     instance = super().create(validated_data)
        #     return instance
        # else:
        #     raise serializers.ValidationError(
        #         {
        #             "status": 400,
        #             "message": "Please Select Valid Student ID",
        #             "data":[]
        #         }
        #     )
        if std_obj:
            validated_data["student_profile"] = std_obj.first()
        else:
            validated_data["student_profile"] = None
            
        instance = super().create(validated_data)
        return instance



class PostRealExamResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentRealExamResult
        fields = "__all__"

    def create(self, validated_data):
        print("serializer request data..")
        print(validated_data)
        print("serializer end request data..")
        std_obj = StudentProfile.objects.filter(application_id=validated_data.get("email"))
        std_objs = std_obj
        if std_obj:
            std = std_obj.first()
            validated_data["student_profile"] = std
            try:
                ManageMasterKey.objects.filter(profile=std, status=False).update(status=True)
            except:
                pass
        else:
            validated_data["student_profile"] = None

        instance = super().create(validated_data)
        
        # try:
        #     ManageMasterKey.objects.filter(user=std_objs.user, status=False).update(status=True)
        # except:
        #     pass

        if std_objs:
            std_profile = std_objs.first()
            total_score = str(round((float(instance.totalscore) / float(instance.totalquestions)) * 100, 2))
            
            if settings.MERITO_STATUS == "True":
                url = settings.MERITO_BASE_URL+"/application/v1/createOrUpdate"

                headers = {
                        "Content-Type": "application/json",
                        "secret-key": settings.MERITO_SECRETE_KEY,
                        "access-key": settings.MERITO_ACCESS_KEY
                    }
                meritto_payload = {
                    "form_id": 22144,
                    "email": std_profile.email,
                    "search_criteria":"email",
                    "data": {
                            "field_349944":total_score
                    }
                }
                print(meritto_payload)
                try:
                    response = requests.post(url, headers=headers, json=meritto_payload)
                    print(response.status_code)
                    print(response.text)
                except Exception as e:
                    print("API Error:", str(e))

        return instance










################# Application meritto bulk upload ##################



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
    ## Added
    identity_proof = serializers.FileField(required=False,allow_null=True)
    tenth_marksheet = serializers.FileField(required=False,allow_null=True)
    twelth_marksheet = serializers.FileField(required=False,allow_null=True)
    graduation_first_marksheet = serializers.FileField(required=False,allow_null=True)
    graduation_second_marksheet = serializers.FileField(required=False,allow_null=True)
    graduation_third_marksheet = serializers.FileField(required=False,allow_null=True)
    graduation_forth_marksheet = serializers.FileField(required=False,allow_null=True)
    graduation_fifth_marksheet = serializers.FileField(required=False,allow_null=True)
    graduation_sixth_marksheet = serializers.FileField(required=False,allow_null=True)
    additional_qualification = serializers.CharField(required=False, allow_blank=True)
    additional_document = serializers.FileField(required=False,allow_null=True)
    co_applicant_pan_card = serializers.FileField(required=False,allow_null=True)
    co_applicant_aadhaar = serializers.FileField(required=False,allow_null=True)
    accounting_profession = models.IntegerField(default=0, null=True)
    co_applicant_profession = models.IntegerField(default=0, null=True)
    co_applicant_sallary_slip = serializers.FileField(required=False,allow_null=True)
    co_applicant_form16 = serializers.FileField(required=False,allow_null=True)
    co_applicant_employee_id_card = serializers.FileField(required=False,allow_null=True)
    co_applicant_passport_size = serializers.FileField(required=False,allow_null=True)
    co_applicant_income_tax_return = serializers.FileField(required=False,allow_null=True)
    co_applicant_compute_income = serializers.FileField(required=False,allow_null=True)
    co_applicant_six_month_bank = serializers.FileField(required=False,allow_null=True)
    co_applicant_agriculture_income = serializers.FileField(required=False,allow_null=True)
    #Added
    resume = serializers.FileField(required=False,allow_null=True)
    guardian_name = serializers.CharField(required=False, allow_null = True)
    guardian_phone = serializers.CharField(required=False, allow_null = True)
    guardian_email = serializers.CharField(required=False, allow_null = True)
    guardian_dropdown = models.IntegerField(default=0, null=True)
    guardian_other_reason = serializers.CharField(required=False, allow_null = True)
    

    class Meta:
        model = StudentProfile
        fields = ["user",'first_name','last_name','email','phone',"state","city","contact_name","contact_phone","date_of_birth","gender","nationality","pincode","address","tenth_passing_year","tenth_passing_percentage","tenth_score_type","tenth_medium","twelveth_passing_year","twelveth_passing_percentage","twelveth_score_type","twelveth_medium","medium_instruction","other_instruction","pg_status","pg_percentage","ug_score_type","institution","higher_education_status","higher_qualification","higher_qualification_institution","employement_status","aadhaar","dob_certificate","photo","signature","user_experience","identity_proof","tenth_marksheet","twelth_marksheet","graduation_first_marksheet","graduation_second_marksheet","graduation_third_marksheet","graduation_forth_marksheet","graduation_fifth_marksheet","graduation_sixth_marksheet","additional_qualification","additional_document","co_applicant_pan_card","co_applicant_aadhaar","accounting_profession","co_applicant_profession","co_applicant_sallary_slip","co_applicant_form16","co_applicant_employee_id_card","co_applicant_passport_size","co_applicant_income_tax_return","co_applicant_compute_income","co_applicant_six_month_bank","co_applicant_agriculture_income","resume","guardian_name","guardian_phone","guardian_email","guardian_dropdown","guardian_other_reason"]
        

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
        print(validate_data)
        user_obj = User.objects.filter(id = validate_data.get('user')).first()
        datas = StudentProfile.objects.filter(user_id = validate_data.get('user')).first()
        exp_payload = {"have_work_ex":"Fresher"}
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
            datas.application_id = user_obj.application_id
            datas.fee_waiver_category = user_obj.fee_waiver_category
            # Added
            datas.identity_proof = validate_data.get('identity_proof',datas.identity_proof)
            datas.tenth_marksheet = validate_data.get('tenth_marksheet',datas.tenth_marksheet)
            datas.twelth_marksheet = validate_data.get('twelth_marksheet',datas.twelth_marksheet)
            datas.graduation_first_marksheet = validate_data.get('graduation_first_marksheet',datas.graduation_first_marksheet)
            datas.graduation_second_marksheet = validate_data.get('graduation_second_marksheet',datas.graduation_second_marksheet)
            datas.graduation_third_marksheet = validate_data.get('graduation_third_marksheet',datas.graduation_third_marksheet)
            datas.graduation_forth_marksheet = validate_data.get('graduation_forth_marksheet',datas.graduation_forth_marksheet)
            datas.graduation_fifth_marksheet = validate_data.get('graduation_fifth_marksheet',datas.graduation_fifth_marksheet)
            datas.graduation_sixth_marksheet = validate_data.get('graduation_sixth_marksheet',datas.graduation_sixth_marksheet)
            datas.additional_qualification = validate_data.get('additional_qualification',datas.additional_qualification)
            datas.additional_document = validate_data.get('additional_document',datas.additional_document)
            datas.accounting_profession = validate_data.get('accounting_profession', datas.accounting_profession)
            datas.co_applicant_pan_card = validate_data.get('co_applicant_pan_card',datas.co_applicant_pan_card)
            datas.co_applicant_aadhaar = validate_data.get('co_applicant_aadhaar',datas.co_applicant_aadhaar)
            datas.co_applicant_profession = validate_data.get('co_applicant_profession',datas.co_applicant_profession)
            datas.co_applicant_sallary_slip = validate_data.get('co_applicant_sallary_slip',datas.co_applicant_sallary_slip)
            datas.co_applicant_form16 = validate_data.get('co_applicant_form16',datas.co_applicant_form16)
            datas.co_applicant_employee_id_card = validate_data.get('co_applicant_employee_id_card',datas.co_applicant_employee_id_card)
            datas.co_applicant_passport_size = validate_data.get('co_applicant_passport_size',datas.co_applicant_passport_size)
            datas.co_applicant_income_tax_return = validate_data.get('co_applicant_income_tax_return',datas.co_applicant_income_tax_return)
            datas.co_applicant_compute_income = validate_data.get('co_applicant_compute_income',datas.co_applicant_compute_income)
            datas.co_applicant_six_month_bank = validate_data.get('co_applicant_six_month_bank',datas.co_applicant_six_month_bank)
            datas.co_applicant_agriculture_income = validate_data.get('co_applicant_agriculture_income',datas.co_applicant_agriculture_income)
            datas.resume = validate_data.get('resume',datas.resume)
            datas.guardian_name = validate_data.get('guardian_name',datas.guardian_name)
            datas.guardian_phone = validate_data.get('guardian_phone',datas.guardian_phone)
            datas.guardian_email = validate_data.get('guardian_email',datas.guardian_email)
            datas.guardian_dropdown = validate_data.get('guardian_dropdown',datas.guardian_dropdown)
            datas.guardian_other_reason = validate_data.get('guardian_other_reason',datas.guardian_other_reason)
            datas.save()
            query = datas
            if len(validate_data.get('user_experience')) > 0:
                num = 1
                exp_payload["have_work_ex"] = "Experienced"
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

                    key1 = f"field_334047_{num}_1"
                    value1 = exp.get('company_name')
                    key2 = f"field_334047_{num}_2"
                    value2 = exp.get('position')
                    key3 = f"field_334047_{num}_3"
                    value3 = exp.get('area')
                    key4 = f"field_334047_{num}_4"
                    value4 = exp.get('start_date').strftime("%d/%m/%Y")
                    key5 = f"field_334047_{num}_5"
                    print("experience.end_date....",experience.end_date)
                    value5 = exp.get('end_date').strftime("%d/%m/%Y") if experience.end_date else exp.get('start_date').strftime("%d/%m/%Y")
                    key6 = f"field_334047_{num}_6"
                    value6 = ""
                    print("values5...",value5)
                    exp_payload[key1] = value1
                    exp_payload[key2] = value2
                    exp_payload[key3] = value3
                    exp_payload[key4] = value4
                    exp_payload[key5] = value5
                    exp_payload[key6] = value6
                    print(exp_payload)
                    num+=1

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
                signature = validate_data.get('signature'),
                application_id = user_obj.application_id,
                fee_waiver_category = user_obj.fee_waiver_category,
                resume = validate_data.get('resume'),
                guardian_name = validate_data.get('guardian_name'),
                guardian_phone = validate_data.get('guardian_phone'),
                guardian_email = validate_data.get('guardian_email'),
                guardian_dropdown = validate_data.get('guardian_dropdown'),
                guardian_other_reason = validate_data.get('guardian_other_reason')
            )
            query.save()
            print(validate_data)
            if len(validate_data.get('user_experience')) > 0:
                num = 1
                exp_payload["have_work_ex"] = "Experienced"
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

                    key1 = f"field_334047_{num}_1"
                    value1 = exp.get('company_name')
                    key2 = f"field_334047_{num}_2"
                    value2 = exp.get('position')
                    key3 = f"field_334047_{num}_3"
                    value3 = exp.get('area')
                    key4 = f"field_334047_{num}_4"
                    value4 = exp.get('start_date').strftime("%d/%m/%Y")
                    key5 = f"field_334047_{num}_5"
                    print("experience.end_date....",experience.end_date)
                    value5 = exp.get('end_date').strftime("%d/%m/%Y") if experience.end_date else exp.get('start_date').strftime("%d/%m/%Y")
                    key6 = f"field_334047_{num}_6"
                    value6 = ""

                    print("values5...",value5)

                    exp_payload[key1] = value1
                    exp_payload[key2] = value2
                    exp_payload[key3] = value3
                    exp_payload[key4] = value4
                    exp_payload[key5] = value5
                    exp_payload[key6] = value6

                    print(exp_payload)
                    
                    num+=1

        if settings.MERITO_STATUS == "True":
            if int(query.gender) == 1:
                mgender = "Male"
            elif int(query.gender) == 2:
                mgender = "Female"
            else:
                mgender = "Other"

            if int(query.tenth_medium) == 1:
                mtmedium = "English"
            elif int(query.tenth_medium) == 2:
                mtmedium = "Hindi"
            else:
                mtmedium = "Other"

            if int(query.twelveth_medium) == 1:
                mthmedium = "English"
            elif int(query.twelveth_medium) == 2:
                mthmedium = "Hindi"
            else:
                mthmedium = "Other"

            if int(query.medium_instruction) == 1:
                minstrmedium = "English"
            elif int(query.medium_instruction) == 2:
                minstrmedium = "Hindi"
            else:
                minstrmedium = "Other"

            if query.higher_education_status == 1:
                higher_status = "Yes"
            else:
                higher_status = "No"

            if query.pg_status == 1:
                pg_status = "Completed"
            else:
                pg_status = "Pursuing"

            if int(query.guardian_dropdown) == 1:
                gname = "Mother"
            elif int(query.guardian_dropdown) == 2:
                gname = "Father"
            else:
                gname = "Other"

            tenth_score_type = query.tenth_score_type if query.tenth_score_type == "Percentage" else "CGPA out of 10"
            twelveth_score_type = query.twelveth_score_type if query.twelveth_score_type == "Percentage" else "CGPA out of 10"
            user_objs = User.objects.filter(id = validate_data.get('user')).first()
            meritto_payload = {
                "form_id": 22144,
                "email": query.email,
                "search_criteria":"email",
                "data": {
                        "first_name":query.first_name,
                        "last_name":query.last_name,
                        "email":query.email,
                        "mobile_no":f"+91-{query.phone}",
                        "father_first_name":"",
                        "father_mobile_no":"",
                        "date_of_birth":query.date_of_birth.strftime("%d/%m/%Y"),
                        "gender":mgender,
                        "nationality":"Indian",
                        "field_339552":query.state,
                        "field_339553":query.city,
                        "field_337926":query.pincode,
                        "field_340085":query.address,
                        "field_340065":query.contact_name,
                        "field_340066":f"+91-{query.contact_phone}",
                        "field_333993_1_1":query.tenth_passing_year,
                        "field_333993_1_2":tenth_score_type,
                        "field_333993_1_3":query.tenth_passing_percentage,
                        "field_333993_1_4":mtmedium,
                        "field_333994_1_1":query.twelveth_passing_year,
                        "field_333994_1_2":twelveth_score_type,
                        "field_333994_1_3":query.twelveth_passing_percentage,
                        "field_333994_1_4":mthmedium,
                        "field_340097_1_1":query.institution,
                        "field_340097_1_2":query.ug_score_type,
                        "field_340097_1_3":query.pg_percentage,
                        "field_340097_1_4":query.pg_percentage,
                        "field_340069":pg_status,
                        "field_340077":higher_status,
                        "field_340079":query.higher_qualification_institution,
                        # "field_340078":query.higher_qualification,
                        "field_342113":query.user.application_id,
                        # "field_343097":"Incomplete",
                        "field_343098":"Complete",
                        "field_349945":user_objs.referral_code,
                        "field_349946":user_objs.referred_code,

                        "field_351358":query.guardian_name,
                        "field_351359":query.guardian_phone,
                        "field_351368":query.guardian_email,
                        "field_351361":gname
                        # "field_351381":query.guardian_other_reason
                }
            }
            if str(gname).lower() == "other":
                other_guardian = {
                    "field_351381":query.guardian_other_reason
                }
                meritto_payload["data"].update(other_guardian)

            print(exp_payload)
            meritto_payload["data"].update(exp_payload) 
            leads = list(DossierData.objects.filter(email=query.email).values_list('id'))
            payment_obj = Payments.objects.filter(dossier_form__in=leads, status="success")
            if payment_obj:
                pay = payment_obj.first()
                payment_payload = {
                    "field_342107":pay.razorpay_signature,
                    "field_342105":pay.razorpay_order_id,
                    "field_342106":pay.razorpay_payment_id,
                    "field_342108":int(pay.amount),
                    "field_342111":"INR",
                    "field_342110":pay.created_at.strftime("%d/%m/%Y %I:%M:%S %p"),
                    "field_342109":"success"
                }
                meritto_payload["data"].update(payment_payload)

            
            print("meritto_payload...",meritto_payload)
            url = settings.MERITO_BASE_URL+"/application/v1/createOrUpdate"

            headers = {
                    "Content-Type": "application/json",
                    "secret-key": settings.MERITO_SECRETE_KEY,
                    "access-key": settings.MERITO_ACCESS_KEY
                }

            try:
                response = requests.post(url, headers=headers, json=meritto_payload)
                print(response.status_code)
                print(response.text)
                ApplicationLog.objects.create(application=query, message=response.text, status=int(response.status_code), activity="creating updating application", datas=validate_data, payload_request=meritto_payload)
            except Exception as e:
                print("API Error:", str(e))

        return query
    



