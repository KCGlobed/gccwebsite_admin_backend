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
from .utils import get_student_score_card_url
from google.cloud import storage
client = storage.Client(project=settings.GS_PROJECT_ID)

from django.db.models import Count
from django.db.models.functions import TruncDate
from utils.google_sheet import get_google_sheet_affliate_seven


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
    resume = serializers.SerializerMethodField("get_resume")
    
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

    # def get_score_card_url(self, obj):
    #     data = get_student_score_card_url(obj.id)
    #     return data
    
    def get_resume(self, obj):
        url = ""
        if obj.resume:
            bucket = client.bucket(
                settings.GS_BUCKET_NAME
            )
            temp_url = f'media/{obj.resume.name}'
            blob = bucket.blob(
                temp_url
            )
            url = blob.public_url
            # print(blob.public_url)
            # url = blob.generate_signed_url(
            #     version="v4",
            #     expiration=timedelta(
            #         days=180
            #     ),
            #     method="GET"
            # )
        return url    

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

class ExperienceDraftSerializer(serializers.Serializer):
    company_name = serializers.CharField(required=False, allow_blank=True)
    position = serializers.CharField(required=False, allow_blank=True)
    area = serializers.CharField(required=False, allow_blank=True)
    start_date = serializers.DateField(required=False, allow_null = True)
    end_date = serializers.DateField(required=False, allow_null = True)

from django.forms.models import model_to_dict
import json
class CompleteStudentProfileByBotSerializer(serializers.ModelSerializer) :
    user_id = serializers.IntegerField(required=True)
    class Meta:
        model = StudentProfile
        fields = ["user_id"]

    def create(self , validate_data):
        draft_obj = StudentProfileDraft.objects.filter(user_id=validate_data.get('user_id'))
        if draft_obj:
            objs = draft_obj.last()
            print("profile draft detail...",objs)
            data_convert = model_to_dict(objs)
            validate_data = data_convert
            exp_payload = {"have_work_ex":"Fresher"}
            query = StudentProfile.objects.filter(user_id=validate_data.get('user'))
            if not query:
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
                    application_id = objs.user.application_id,
                    fee_waiver_category = objs.user.fee_waiver_category,
                    resume = validate_data.get('resume'),
                    resume_key_status = validate_data.get('resume_key_status'),
                    guardian_name = validate_data.get('guardian_name'),
                    guardian_phone = validate_data.get('guardian_phone'),
                    guardian_email = validate_data.get('guardian_email'),
                    guardian_dropdown = validate_data.get('guardian_dropdown'),
                    guardian_other_reason = validate_data.get('guardian_other_reason'),
                    guardian_key_status = validate_data.get('guardian_key_status')
                )
                query.save()
                print(validate_data)
                exp_datas = StudentExperienceDraft.objects.filter(student_profile_id=objs.id)
                if exp_datas.exists():
                    exp_data_list = [model_to_dict(i) for i in exp_datas]
                    validate_data['user_experience'] = exp_data_list
                    print("expeee converted...", validate_data.get("user_experience"))
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

                    if query.guardian_dropdown:
                        if int(query.guardian_dropdown) == 1:
                            gname = "Mother"
                        elif int(query.guardian_dropdown) == 2:
                            gname = "Father"
                        else:
                            gname = "Other"
                    else:
                        gname = ""
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
                                "field_343098":"Complete",
                                "field_349945":query.referral_code,
                                "field_349946":query.referred_code,

                                # "field_351358":query.guardian_name,
                                # "field_351359":query.guardian_phone,
                                # "field_351368":query.guardian_email,
                                "field_351358":query.guardian_name if query.guardian_name else "",
                                "field_351359":query.guardian_phone if query.guardian_phone else "",
                                "field_351368":query.guardian_email if query.guardian_email else "",
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
                    except Exception as e:
                        print("API Error:", str(e))
                
                return query
        return serializers.ValidationError("Invalid request")
        




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
        serializer = ExperienceDraftSerializer(data=value, many=True)
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

class StudentExperienceDraftRelationSerializer(serializers.ModelSerializer):
    
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
    interview_detail = serializers.SerializerMethodField("get_interview_detail")
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
                dt2 = datetime.combine(obj.slot_date, target_time)
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
        if obj.slot_date:
            if obj.slot_date == datetime.now().date():
                start_str, end_str = obj.slot_time.split(" - ")
                current_time = datetime.now().time().replace(microsecond=0)
                target_time = datetime.strptime(start_str, "%I:%M %p").time()
                dt1 = datetime.combine(date.today(), current_time)
                dt2 = datetime.combine(date.today(), target_time)

                print(dt1, dt2)
                if dt1>dt2:
                    current_time = datetime.now().time().replace(microsecond=0)
                    target_time = datetime.strptime(end_str, "%I:%M %p").time()
                    dt1 = datetime.combine(date.today(), current_time)
                    dt2 = datetime.combine(date.today(), target_time)
                    if dt1<dt2:
                        print(dt1, dt2)
                        std_exam  = ManageMasterKey.objects.filter(profile=obj.id, status=False, created_at__date=datetime.now().date())
                        if std_exam:
                            result   = std_exam.last()
                            exam_url = result.exam_url

        return exam_url
    

    def get_interview_detail(self, obj):
        interview_objs  = ManageStudentInterview.objects.filter(profile=obj.id)
        interview_data  = StudentprofileCustomFieldInterviewSerializer(interview_objs, many=True).data
        return interview_data
    
    
    class Meta:
        model = StudentProfile
        fields = "__all__"



class StudentprofileCustomFieldInterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManageStudentInterview
        fields = ["interview_date","company","package_status"]



class StudentProfileListSerializer(serializers.ModelSerializer):
    student_experience = serializers.SerializerMethodField()
    exam_status = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    application_id = serializers.SerializerMethodField("get_application_id")
    student_result = serializers.SerializerMethodField("get_student_result")
    result_status = serializers.SerializerMethodField("get_result_status")
    referral_code = serializers.SerializerMethodField("get_referral_code")
    referred_code = serializers.SerializerMethodField("get_referred_code")
    exam_url = serializers.SerializerMethodField("get_exam_url")
    guardian_dropdown = serializers.SerializerMethodField("get_guardian_dropdown")
    interview_detail = serializers.SerializerMethodField("get_interview_detail")

    def get_guardian_dropdown(self, obj):
        return obj.get_guardian_dropdown_display()

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
    
    def get_interview_detail(self, obj):
        interview_objs  = ManageStudentInterview.objects.filter(profile=obj.id)
        interview_data  = StudentprofileCustomFieldInterviewSerializer(interview_objs, many=True).data

        return interview_data
    
    def get_exam_url(self, obj):
        exam_url = ""
        if obj.slot_date:
            if obj.slot_date == datetime.now().date():
                start_str, end_str = obj.slot_time.split(" - ")
                current_time = datetime.now().time().replace(microsecond=0)
                target_time = datetime.strptime(start_str, "%I:%M %p").time()
                dt1 = datetime.combine(date.today(), current_time)
                dt2 = datetime.combine(date.today(), target_time)

                print(dt1, dt2)
                if dt1>dt2:
                    current_time = datetime.now().time().replace(microsecond=0)
                    target_time = datetime.strptime(end_str, "%I:%M %p").time()
                    dt1 = datetime.combine(date.today(), current_time)
                    dt2 = datetime.combine(date.today(), target_time)
                    if dt1<dt2:
                        print(dt1, dt2)
                        std_exam  = ManageMasterKey.objects.filter(profile=obj.id, status=False, created_at__date=datetime.now().date())
                        if std_exam:
                            result   = std_exam.last()
                            exam_url = result.exam_url

        return exam_url
    
    
    class Meta:
        model = StudentProfile
        fields = "__all__"


class StudentProfileDraftSerializer(serializers.ModelSerializer):
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
        answe = StudentExperienceDraft.objects.filter(student_profile_id =obj.id).order_by("id")
        return StudentExperienceDraftRelationSerializer(answe, many=True).data
    
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
        model = StudentProfileDraft
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



class WebhookCreatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = "__all__"

    def create(self, validated_data):
        print("webhook request....",validated_data)
        if not Payments.objects.filter(razorpay_payment_id=validated_data.get('razorpay_payment_id')).exists():
            validated_data["response"] = json.loads(validated_data["response"])        
            validated_data["amount"] = float(validated_data["amount"])         
            validated_data["created_at"] = timezone.now()           
            validated_data["updated_at"] = timezone.now()   
            instance = super().create(validated_data)

            url = settings.CSRF_TRUSTED_ORIGINS[0]+"/api/users/create_student/"

            payload = {
                "full_name": instance.dossier_form.full_name,
                "email": instance.dossier_form.email,
                "phone1": instance.dossier_form.phone
            }
            try:
                print("user....",payload)
                response = requests.post(url, json=payload)
                print(response.status_code)
                print(response.text)
                User.objects.filter(email=instance.dossier_form.email).update(city=instance.dossier_form.city, state=instance.dossier_form.state, fee_waiver_category=instance.dossier_form.fee_waiver_category)
                # DossierLog.objects.create(dossier=instance, message=response.text, status=int(response.status_code), activity="creating", datas=validated_data)
            except Exception as e:
                print("API Error:", str(e)) 


            return instance
        return validated_data


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


class StudentProfileCreatePaymentSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(required=True)
    class Meta:
        model = StudentPayment
        fields = "__all__"

    def create(self, validated_data):
        print("serializer payment request data..")
        print(validated_data)
        
        validated_data["response"] = json.loads(validated_data["response"])         
        validated_data["amount"] = float(validated_data["amount"])         
        validated_data["created_at"] = timezone.now()           
        validated_data["updated_at"] = timezone.now()   
        instance = super().create(validated_data)
        print("instance...", instance)

        if str(validated_data.get("amount")).lower() == "success":
            interview_obj = ManageStudentInterview.objects.filter(student_id=validated_data.get('student_id')).first()
            interview_obj.payment_amount = float(validated_data["amount"])
            interview_obj.payment_status = True
            interview_obj.save()
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
                            "field_349944":total_score,
                            "field_351644":"Appeared"
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
    #Added
    resume = serializers.FileField(required=False,allow_null=True)
    guardian_name = serializers.CharField(required=False, allow_null = True)
    guardian_phone = serializers.CharField(required=False, allow_null = True)
    guardian_email = serializers.CharField(required=False, allow_null = True)
    guardian_dropdown = models.IntegerField(default=0, null=True)
    guardian_other_reason = serializers.CharField(required=False, allow_null = True)
    

    class Meta:
        model = StudentProfile
        fields = ["user",'first_name','last_name','email','phone',"state","city","contact_name","contact_phone","date_of_birth","gender","nationality","pincode","address","tenth_passing_year","tenth_passing_percentage","tenth_score_type","tenth_medium","twelveth_passing_year","twelveth_passing_percentage","twelveth_score_type","twelveth_medium","medium_instruction","other_instruction","pg_status","pg_percentage","ug_score_type","institution","higher_education_status","higher_qualification","higher_qualification_institution","employement_status","aadhaar","dob_certificate","photo","signature","user_experience","resume","guardian_name","guardian_phone","guardian_email","guardian_dropdown","guardian_other_reason"]
        

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
                    # print("values5...",value5)
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

                    # print("values5...",value5)

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
            
            if query.guardian_dropdown:
                if int(query.guardian_dropdown) == 1:
                    gname = "Mother"
                elif int(query.guardian_dropdown) == 2:
                    gname = "Father"
                else:
                    gname = "Other"
            else:
                gname = ""

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
                        "field_340066":f"+91-{query.contact_phone}" if query.contact_phone else "",
                        "field_333993_1_1":query.tenth_passing_year,
                        "field_333993_1_2":tenth_score_type,
                        "field_333993_1_3":query.tenth_passing_percentage,
                        "field_333993_1_4":mtmedium,
                        "field_333994_1_1":query.twelveth_passing_year,
                        "field_333994_1_2":twelveth_score_type,
                        "field_333994_1_3":query.twelveth_passing_percentage,
                        "field_333994_1_4":mthmedium,
                        "field_340097_1_1":str(query.institution).replace("’",""),
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

                        # "field_351358":query.guardian_name,
                        # "field_351359":query.guardian_phone,
                        # "field_351368":query.guardian_email,
                        "field_351358":query.guardian_name if query.guardian_name else "",
                        "field_351359":query.guardian_phone if query.guardian_phone else "",
                        "field_351368":query.guardian_email if query.guardian_email else "",
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

            std_result = StudentRealExamResult.objects.filter(student_profile=query)
            if std_result:
                meritto_payload["data"]["field_351644"] = "Appeared"
            # else:
            #     meritto_payload["data"]["field_351644"] = "Not Appeared"
            
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
    



class CompleteStudentDraftSerializer(serializers.ModelSerializer) :
    user = serializers.IntegerField(required=True)
    first_name = serializers.CharField(max_length = 255, required=False)
    last_name = serializers.CharField(max_length = 255, required=False)
    email = serializers.CharField(max_length = 255, required=False)
    phone = serializers.CharField(max_length = 255, required=False)
    state = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    contact_name = serializers.CharField(required=False, allow_blank=True)
    contact_phone = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null = True)
    gender = serializers.IntegerField(required=False, allow_null=True)
    nationality = serializers.CharField(required=False, allow_blank=True)
    pincode = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    tenth_passing_year = serializers.IntegerField(required=False, allow_null = True)
    tenth_passing_percentage = serializers.FloatField(required=False, allow_null = True)
    tenth_score_type = serializers.CharField(required=False, allow_null = True)
    tenth_medium = serializers.IntegerField(required=False, default=0)
    twelveth_passing_year = serializers.IntegerField(required=False, allow_null = True)
    twelveth_passing_percentage = serializers.FloatField(required=False, allow_null = True)
    twelveth_score_type = serializers.CharField(required=False, allow_null = True)
    twelveth_medium = serializers.IntegerField(required=False, default = 0)
    medium_instruction = serializers.IntegerField(required=False, default=0)
    other_instruction = serializers.CharField(required=False, allow_null=True)
    pg_status = serializers.IntegerField(required=False, default=0)
    pg_percentage = serializers.FloatField(required=False, allow_null = True)
    ug_score_type = serializers.CharField(required=False, allow_null = True)
    institution = serializers.CharField(required=False, allow_null=True)
    higher_education_status = serializers.IntegerField(required=False, default=0)
    higher_qualification = serializers.CharField(required=False, allow_null=True)
    higher_qualification_institution = serializers.CharField(required=False, allow_null=True)
    employement_status = serializers.IntegerField(required=False, default=0)
    # higher_qualification_institution = serializers.CharField(required=False, allow_null=True)
    aadhaar = serializers.FileField(required=False,allow_null=True)
    dob_certificate = serializers.FileField(required=False,allow_null=True)
    photo = serializers.FileField(required=False,allow_null=True)
    signature = serializers.FileField(required=False,allow_null=True)
    user_experience = serializers.JSONField(required=False,  allow_null=True)
    #Added
    resume = serializers.FileField(required=False,allow_null=True)
    guardian_name = serializers.CharField(required=False, allow_null = True)
    guardian_phone = serializers.CharField(required=False, allow_null = True)
    guardian_email = serializers.CharField(required=False, allow_null = True)
    guardian_dropdown = models.IntegerField(default=0, null=True)
    guardian_other_reason = serializers.CharField(required=False, allow_blank = True)
    

    class Meta:
        model = StudentProfileDraft
        fields = ["user",'first_name','last_name','email','phone',"state","city","contact_name","contact_phone","date_of_birth","gender","nationality","pincode","address","tenth_passing_year","tenth_passing_percentage","tenth_score_type","tenth_medium","twelveth_passing_year","twelveth_passing_percentage","twelveth_score_type","twelveth_medium","medium_instruction","other_instruction","pg_status","pg_percentage","ug_score_type","institution","higher_education_status","higher_qualification","higher_qualification_institution","employement_status","aadhaar","dob_certificate","photo","signature","user_experience","resume","guardian_name","guardian_phone","guardian_email","guardian_dropdown","guardian_other_reason"]
        

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
        serializer = ExperienceDraftSerializer(data=value, many=True)
        if serializer.is_valid():
            return serializer.validated_data
        raise serializers.ValidationError(serializer.errors)


    def create(self , validate_data):
        print(validate_data)
        user_obj = User.objects.filter(id = validate_data.get('user')).first()
        datas = StudentProfileDraft.objects.filter(user_id = validate_data.get('user')).first()
        exp_payload = {"have_work_ex":"Fresher"}
        print(validate_data.get('user_experience'))
        print(type(validate_data.get('user_experience')))
        print("create update")
        if datas is not None:
            print("select update")
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
            datas.resume = validate_data.get('resume',datas.resume)
            datas.guardian_name = validate_data.get('guardian_name',datas.guardian_name)
            datas.guardian_phone = validate_data.get('guardian_phone',datas.guardian_phone)
            datas.guardian_email = validate_data.get('guardian_email',datas.guardian_email)
            datas.guardian_dropdown = validate_data.get('guardian_dropdown',datas.guardian_dropdown)
            datas.guardian_other_reason = validate_data.get('guardian_other_reason',datas.guardian_other_reason)
            datas.save()
            query = datas
            exp_val = validate_data.get('user_experience')
            if exp_val and exp_val!="":
                if len(validate_data.get('user_experience')) > 0:
                    num = 1
                    exp_payload["have_work_ex"] = "Experienced"
                    StudentExperienceDraft.objects.filter(student_profile = query).delete()
                    for exp in validate_data.get('user_experience'):
                        experience = StudentExperienceDraft(
                            student_profile = query,
                            position = exp.get('position'),
                            company_name = exp.get('company_name'),
                            area = exp.get('area'),
                            start_date = exp.get('start_date'),
                            end_date = exp.get('end_date'),

                        )
                        experience.save()

                        num+=1

        else:
            print("select create")
            query = StudentProfileDraft(
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
            print("before saving")
            query.save()
            print(validate_data)
            exp_val = validate_data.get('user_experience')
            if exp_val and exp_val!="":
                if len(validate_data.get('user_experience')) > 0:
                    num = 1
                    exp_payload["have_work_ex"] = "Experienced"
                    for exp in validate_data.get('user_experience'):
                        experience = StudentExperienceDraft(
                            student_profile = query,
                            position = exp.get('position'),
                            company_name = exp.get('company_name'),
                            area = exp.get('area'),
                            start_date = exp.get('start_date'),
                            end_date = exp.get('end_date'),

                        )
                        experience.save()
                    
                        num+=1
        return query

########################## INETRVIEW ############################






class CompanyInterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyMaster
        fields = ["id","name"]



class StudentInterviewCreateOrUpdateSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(required=True)
    company = serializers.CharField(max_length = 255, required=False)
    attempt_status = serializers.IntegerField(required=False)
    absent_reason = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    result = serializers.IntegerField(required=False)
    interview_date = serializers.DateField(required=False, allow_null = True)
    package_status = serializers.BooleanField(required=False, allow_null = True)

    class Meta:
        model = ManageStudentInterview
        fields = ["student_id","company","attempt_status","absent_reason","result","interview_date","package_status"]

    def validate(self, validate_data):
        datas = StudentProfile.objects.filter(id = validate_data.get('student_id'))
        if not datas:
            # raise serializers.ValidationError("Invalid Student ID")
            raise serializers.ValidationError({
                "status": 400,
                "message": "Invalid Student ID",
                "data": {}
            })
        return validate_data
    
    def create(self , validate_data):
        print(validate_data)
        objs = ManageStudentInterview.objects.filter(profile=validate_data.get('student_id'))
        if objs:
            instance = objs.first()    
            instance.company_id = validate_data.get('company', instance.company.id)    
            instance.interview_date = validate_data.get('interview_date', instance.interview_date)    
            instance.attempt_status = validate_data.get('attempt_status', instance.attempt_status)    
            instance.absent_reason = validate_data.get('absent_reason', instance.absent_reason) if validate_data.get('attempt_status') == 2 else ""   
            instance.result = validate_data.get('result', instance.result)    
            instance.package_status = validate_data.get('package_status', instance.package_status)    
            instance.save()
        else:
            instance = ManageStudentInterview(
               profile_id = validate_data.get('student_id'),  
               company_id = validate_data.get('company') if validate_data.get('company') else 6,
               interview_date = validate_data.get('interview_date')
            )
            instance.save()
        

        if settings.MERITO_STATUS == "True":
            meritto_payload = {
                "form_id": 22144,
                "email": instance.profile.email,
                "search_criteria":"email",
                "data": {
                        "field_352367":instance.company.name,
                        "field_352366":instance.interview_date.strftime("%d/%m/%Y %I:%M:%S %p")
                    }
            }
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
                ApplicationLog.objects.create(application_id=validate_data.get('student_id'), message=response.text, status=int(response.status_code), activity="Schedule Interview", datas=validate_data, payload_request=meritto_payload)
            except Exception as e:
                print("API Error:", str(e))

        ManageStudentInterviewHistory.objects.create(profile=instance.profile, company=instance.company, attempt_status=instance.attempt_status, absent_reason=instance.absent_reason, result=instance.result, interview_date=instance.interview_date, interview_time=instance.interview_time, package_status=instance.package_status,payment_status=instance.payment_status,payment_amount=instance.payment_amount,remark="profile")
        return instance
        



class StudentProfileInterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ["id","first_name","last_name","email","phone","application_id"]


class StudentInterviewSerializer(serializers.ModelSerializer):
    attempt_status = serializers.SerializerMethodField('get_attempt_status')
    result = serializers.SerializerMethodField('get_result')
    company_detail = serializers.SerializerMethodField('get_company_detail')

    class Meta:
        model = ManageStudentInterview
        fields = ["attempt_status","interview_date","absent_reason","result","created_at", "company_detail", "payment_status"]


    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Fetch related form
        std_obj = StudentProfile.objects.filter(id=instance.profile.id).first()

        if std_obj:
            form_data = StudentProfileInterviewSerializer(std_obj).data
            # Merge form fields into main response
            data.update(form_data)
            
        return data

    def get_attempt_status(self, value):
        return value.get_attempt_status_display()
    def get_result(self, value):
        return value.get_result_display()

    def get_company_detail(self, value):
        cmp_obj = CompanyMaster.objects.filter(id=value.company.id)
        cmpy_data = CompanyInterviewSerializer(cmp_obj, many=True).data
        return cmpy_data


class StudentInterviewReportSerializer(serializers.ModelSerializer):
    attempt_status = serializers.SerializerMethodField('get_attempt_status')
    result = serializers.SerializerMethodField('get_result')
    company_name = serializers.SerializerMethodField('get_company_name')

    class Meta:
        model = ManageStudentInterview
        fields = ["attempt_status","interview_date","absent_reason","result","created_at", "company_name", "payment_status"]


    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Fetch related form
        std_obj = StudentProfile.objects.filter(id=instance.profile.id).first()

        if std_obj:
            form_data = StudentProfileInterviewSerializer(std_obj).data
            # Merge form fields into main response
            data.update(form_data)
            
        return data

    def get_attempt_status(self, value):
        return value.get_attempt_status_display()
    def get_result(self, value):
        return value.get_result_display()

    def get_company_name(self, value):
        print(value)
        return value.company.name




class StudentInterviewCreateSerializer(serializers.ModelSerializer):
    lid = serializers.IntegerField(required=True)
    interview_date = serializers.DateField(required=True)

    class Meta:
        model = ManageStudentInterview
        fields = ["lid","interview_date"]

    def create(self, validate_data):
        lobj = DossierData.objects.filter(id=validate_data.get('lid')).first()
        lobj.interview_date=validate_data.get('interview_date')
        lobj.save()
        # print(lobj)
        src_type = lobj.source
        if settings.EXCEL_INPUT == "True":
            if src_type == 15:
                print("sheet enter")
                try:
                    sheet = get_google_sheet_affliate_seven()
                    print("open sheet...",sheet)
                    # local_time = timezone.localtime(lobj.interview_date)
                    # create_times = local_time.strftime("%Y-%m-%d %H:%M:%S")
                    # lobj.interview_date
                    selected_date = lobj.interview_date.strftime("%Y-%m-%d")
                    row_data = [
                        "Yes",
                        selected_date
                    ]

                    # find email in column B
                    cell = sheet.find(lobj.phone)

                    if cell:
                        row_number = cell.row
                        print("row found:", row_number)
                        sheet.update(f"K{row_number}:L{row_number}", [row_data])
                        print(f"Row {row_number} updated successfully")

                        print("row updated successfully")

                    else:
                        print("row not found, new row inserted")
                except Exception as e:
                    print("google sheet error", str(e))

        return validate_data


    # def validate(self, validate_data):
    #     lobj = DossierData.objects.filter(id=validate_data.get('lid')).first()
    #     datas = StudentProfile.objects.filter(email = lobj.email)
    #     if datas:
    #         # raise serializers.ValidationError("Invalid Student ID")
    #         raise serializers.ValidationError({
    #             "status": 400,
    #             "message": "Already Scheduled Interview",
    #             "data": {}
    #         })
    #     return validate_data
    
    # def create(self , validate_data):
    #     print(validate_data)
    #     lobj = DossierData.objects.filter(id=validate_data.get('lid')).first()
    #     if lobj:
    #         user_obj = User.objects.filter(email=lobj.email).first()
    #         name = str(user_obj.first_name).split(" ")
    #         fname = name[0]
    #         if not user_obj.last_name:
    #             lname = " ".join(name[1:])

    #         std_draft = StudentProfileDraft.objects.filter(user=user_obj)
    #         if not std_draft:
    #             draft_obj = StudentProfileDraft(user=user_obj, email=user_obj.email, first_name=fname,last_name=lname, phone=user_obj.phone1,city=user_obj.city,state=user_obj.state, application_id=user_obj.application_id,fee_waiver_category = user_obj.fee_waiver_category)
    #             draft_obj.save()

    #         std_profile = StudentProfile.objects.filter(user=user_obj)
    #         if not std_profile:
    #             profile_obj = StudentProfile(user=user_obj, email=user_obj.email, first_name=fname,last_name=lname, phone=user_obj.phone1,city=user_obj.city,state=user_obj.state, application_id=user_obj.application_id,fee_waiver_category = user_obj.fee_waiver_category)
    #             profile_obj.save()
    #         else:
    #             profile_obj = std_profile.first()
            
    #         interview_obj = ManageStudentInterview.objects.filter(profile_id=profile_obj.id)
    #         if not interview_obj:
    #             instance = ManageStudentInterview(
    #             profile_id = profile_obj.id,  
    #             company_id = 6,
    #             interview_date = validate_data.get('interview_date')
    #             )
    #             instance.save()
    #         else:
    #             instance = interview_obj.first()
    #             instance.interview_date = validate_data.get('interview_date')
    #             instance.save()
        
    #         if settings.MERITO_STATUS == "True":
    #             meritto_payload = {
    #                 "form_id": 22144,
    #                 "email": instance.profile.email,
    #                 "search_criteria":"email",
    #                 "data": {
    #                         "first_name":profile_obj.first_name,
    #                         "last_name":profile_obj.last_name,
    #                         "email":profile_obj.email,
    #                         "mobile_no":f"+91-{profile_obj.phone}",
    #                         "field_339552":profile_obj.state,
    #                         "field_339553":profile_obj.city,
    #                         "field_352367":instance.company.name,
    #                         "field_352366":instance.interview_date.strftime("%d/%m/%Y %I:%M:%S %p")
    #                     }
    #             }
    #             url = settings.MERITO_BASE_URL+"/application/v1/createOrUpdate"

    #             headers = {
    #                     "Content-Type": "application/json",
    #                     "secret-key": settings.MERITO_SECRETE_KEY,
    #                     "access-key": settings.MERITO_ACCESS_KEY
    #                 }

    #             try:
    #                 response = requests.post(url, headers=headers, json=meritto_payload)
    #                 print(response.status_code)
    #                 print(response.text)
    #                 ApplicationLog.objects.create(application_id=profile_obj.id, message=response.text, status=int(response.status_code), activity="Schedule Interview Directly", datas=validate_data, payload_request=meritto_payload)
    #             except Exception as e:
    #                 print("API Error:", str(e))

    #         ManageStudentInterviewHistory.objects.create(profile=instance.profile, company=instance.company, attempt_status=instance.attempt_status, absent_reason=instance.absent_reason, result=instance.result, interview_date=instance.interview_date, interview_time=instance.interview_time, package_status=instance.package_status,payment_status=instance.payment_status,payment_amount=instance.payment_amount,remark="lead")
    #         return instance
    #     raise serializers.ValidationError("Invalid Request")
        
