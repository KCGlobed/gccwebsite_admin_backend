from rest_framework import serializers
from users.models import *
from students.models import Payments
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator 
from django.utils.encoding import smart_str, force_bytes

from django.conf import settings
from django.core.mail import send_mail
from gcc_backend.utils import *
from django.template import loader
from datetime import datetime, date
import requests
from django.utils import timezone
from career.models import DossierData
from django.db.models import Count
from django.db.models.functions import TruncDate
from students.models import *
from datetime import datetime, timedelta, date

class WebsiteUserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length = 255,required=True)
    password = serializers.CharField(max_length = 255,required=True)
    role = serializers.CharField(max_length = 255,required=True)
    # device_type = serializers.CharField(max_length = 255, required=True)
    # device_id = serializers.CharField(max_length = 255, required=True)

    class Meta:
        model = User
        fields = ['email', 'password',"role"]

    def validate(self, data):
        user = User.objects.filter(email =data.get('email').lower(), role=User.Student).first()
        if user is None:
            raise serializers.ValidationError("User Not found with this email!")
        
        if user.is_active is False:
            ManageLoginForm.objects.create(user=user,status="User is not active!",cred=data.get('password'))
            user.failed_login_attempts+=1
            user.save()
            raise serializers.ValidationError("User is not active!")
        
        if user.email_verified == 0:
            ManageLoginForm.objects.create(user=user,status="User email is not verified!",cred=data.get('password'))
            user.failed_login_attempts+=1
            user.save()
            raise serializers.ValidationError("User email is not verified!")
        
        if user:
            if not user.check_password(data.get('password')):
                ManageLoginForm.objects.create(user=user,status="Invalid Password!",cred=data.get('password'))
                user.failed_login_attempts+=1
                user.save()
                raise serializers.ValidationError("Invalid Password!")
            
        if str(user.get_role_display()).lower() != str(data.get('role')).lower():
            ManageLoginForm.objects.create(user=user,status="Invalid Account Role",cred=data.get('password'))
            user.failed_login_attempts+=1
            user.save()
            raise serializers.ValidationError("Invalid Account")
        
        return data


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length = 255,required=True)
    password = serializers.CharField(max_length = 255,required=True)
    role = serializers.CharField(max_length = 255,required=True)
    # device_type = serializers.CharField(max_length = 255, required=True)
    # device_id = serializers.CharField(max_length = 255, required=True)

    class Meta:
        model = User
        fields = ['email', 'password',"role"]

    def validate(self, data):
        user = User.objects.filter(email =data.get('email').lower()).first()
        if user is None:
            raise serializers.ValidationError("User Not found with this email!")
        
        if user.is_active is False:
            ManageLoginForm.objects.create(user=user,status="User is not active!",cred=data.get('password'))
            user.failed_login_attempts+=1
            user.save()
            raise serializers.ValidationError("User is not active!")
        
        if user.email_verified == 0:
            ManageLoginForm.objects.create(user=user,status="User email is not verified!",cred=data.get('password'))
            user.failed_login_attempts+=1
            user.save()
            raise serializers.ValidationError("User email is not verified!")
        
        if user:
            if not user.check_password(data.get('password')):
                ManageLoginForm.objects.create(user=user,status="Invalid Password!",cred=data.get('password'))
                user.failed_login_attempts+=1
                user.save()
                raise serializers.ValidationError("Invalid Password!")
        if str(user.get_role_display()).lower() != str(data.get('role')).lower():
            ManageLoginForm.objects.create(user=user,status="Invalid Account Role",cred=data.get('password'))
            user.failed_login_attempts+=1
            user.save()
            raise serializers.ValidationError("Invalid Account")
        
        return data



# def send_email_async(subject, message, email_from, recipient_list, html_message):
#     print("start calling")
#     # send_mail(
#     #     subject,
#     #     message,
#     #     email_from,
#     #     recipient_list,
#     #     html_message=html_message,
#     #     fail_silently=False
#     # )
#     subject = 'GCC School – Payment Confirmation & Next Steps for NFET 2026'

#     message = f''
#     email_from = settings.DEFAULT_FROM_EMAIL
#     recipient_list = [user.email, ]
#     html_message = loader.render_to_string(
#         'user_login_detail_email.html',
#         {
#             'name': user.first_name,
#             'candidate_id': generate_application_id,
#             'slot_booking': 'https://forms.gle/UQqKnCsmJzVLK6qU8',
#             'website_url': settings.WEBSITE_BASE_URL,
#             'login_url': settings.WEBSITE_BASE_URL+"/login",
#             "email": user.email,
#             "password": password,               

#         }
#     )

#     send_mail( subject, message, email_from, recipient_list,html_message=html_message )

#     print("end calling")




import random
import string
import re

# def generate_referral_code():
#     characters = string.ascii_uppercase + string.digits
#     return ''.join(random.choices(characters, k=20))

def generate_referral_code(full_name):
    # Validate name: only letters and spaces allowed
    # if not re.match(r'^[A-Za-z ]+$', full_name):
    #     raise ValueError("Full name should contain only alphabets and spaces.")

    # Remove spaces and convert to uppercase
    cleaned_name = full_name.replace(" ", "").upper()


    # Take first 4 characters
    name_part = cleaned_name[:4]

    # Generate 5 random alphanumeric characters
    random_part = ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=5)
    )

    # Final referral code
    return f"{name_part}_{random_part}"



class CreateStudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length = 255, required=True)
    email = serializers.EmailField(max_length = 255, required=True)
    city = serializers.CharField(max_length = 255, required=False, allow_blank=True)
    state = serializers.CharField(max_length = 255, required=False, allow_blank=True)
    country = serializers.CharField(max_length = 255, required=False, allow_blank=True)
    phone1 = serializers.CharField(max_length = 255, required=False, allow_blank=True)
    referred_code = serializers.CharField(max_length = 255, required=False, allow_blank=True)
    class Meta:
        model = User
        fields = ['email','full_name',"city","state","country","phone1","referred_code"]
        

    def validate(self, data):
        user_count = User.objects.filter(email = data.get('email').lower()).count()
        if user_count > 0:
            raise serializers.ValidationError('Email address is already registered with Us')
        
        return data


    def create(self, validate_data):
        password = generate_random_password(8)
        info = { "first_name": validate_data.get('full_name'), "last_name":"", 'email': validate_data.get('email').lower(), 'password': password}
        user = User.objects.create_user(**info)
        self.generated_password = password
        # assign_role(user, "Student")
        waive_value = ""
        pay_obj = Payments.objects.filter(dossier_form__email=validate_data.get('email'), status="success")
        if pay_obj:
            pay_obj = pay_obj.last()
            waive_value = pay_obj.fee_waiver_category
        else:
            pay_obj = DossierData.objects.filter(email=validate_data.get('email'))
            if pay_obj:
                pay_obj = pay_obj.last()
                waive_value = pay_obj.fee_waiver_category

        refferals_code = generate_referral_code(validate_data.get('full_name'))


        formatted_emp = str(user.id).zfill(4)
        formatted_month = str(datetime.now().date().month).zfill(2)
        formatted_year = str(datetime.now().date().year)
        generate_application_id = f"NFET-{formatted_year}-{formatted_month}{formatted_emp}"  # 000001
        user.role = User.Student
        user.email_verified = 1
        user.is_active = True
        user.country = validate_data.get('country')
        user.state = validate_data.get('state')
        user.city = validate_data.get('city')
        user.phone1 = validate_data.get('phone1')
        user.application_id = generate_application_id
        user.fee_waiver_category = waive_value
        user.referral_code = refferals_code
        user.referred_code = validate_data.get('referred_code')
        user.save()
        num = user.id

        if validate_data.get('referred_code'):
            used_by_user = User.objects.filter(referral_code=validate_data.get('referred_code')).first()
            if used_by_user:
                reff = ManageReferal(user=user, used_by=used_by_user, referral_code=validate_data.get('referred_code'))
            else:
                reff = ManageReferal(user=user, used_by=None, referral_code=validate_data.get('referred_code'))
            reff.save()

        DossierData.objects.filter(email=validate_data.get('email').lower()).update(referral_code=refferals_code)
        ManageStudentExtraDetail.objects.create(
                user=user,
                cred=password
                )

        if settings.MERITO_STATUS == "True":
            
            # API URL
            url = settings.MERITO_BASE_URL+"/lead/v1/createOrUpdate"

            headers = {
                "Content-Type": "application/json",
                "secret-key": settings.MERITO_SECRETE_KEY,
                "access-key": settings.MERITO_ACCESS_KEY
            }

            payload = {
                "email": user.email,
                "search_criteria": "email",
                "cf_payment_status":"Complete",
                "cf_refferal_code":validate_data.get('referred_code'),
                "cf_reference_code":refferals_code,
                "cf_gcc_application_number":generate_application_id
            }
            print("user create meritto payload...",payload)
            try:
                response = requests.post(url, headers=headers, json=payload)
                print(response.status_code)
                print(response.text)
            except Exception as e:
                print("API Error:", str(e))

        subject = 'Welcome to GCC School. Here are your login details.'

        message = f''
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email, ]
        html_message = loader.render_to_string(
            'user_login_detail_email.html',
            {
                'name': user.first_name,
                'candidate_id': generate_application_id,
                'slot_booking': 'https://forms.gle/UQqKnCsmJzVLK6qU8',
                'website_url': settings.WEBSITE_BASE_URL,
                'login_url': settings.WEBSITE_BASE_URL+"/login",
                "email": user.email,
                "password": password,               

            }
        )

        send_mail( subject, message, email_from, recipient_list,html_message=html_message )

        return user


class UpdateStudentSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length = 255, required=True)
    lid = serializers.CharField(max_length = 255, required=True)
    phone = serializers.CharField(max_length = 255, required=False)
    class Meta:
        model = User
        fields = ['email','lid','phone']
        

    # def validate(self, data):
    #     user_count = User.objects.filter(email = data.get('email').lower()).count()
    #     if user_count > 0:
    #         raise serializers.ValidationError('Email address is already registered with Us')
    #     return data


    def create(self, validate_data):
        password = generate_random_password(8)
        self.generated_password = password
        lead = DossierData.objects.filter(id=validate_data.get('lid'))
        if lead:
            lead_obj = lead.first()
            # user_profile = .objects.filter(email=str(lead_obj.email).lower())
            # if user:
            user = User.objects.filter(email=str(lead_obj.email).lower())
            if user:
                u_obj = user.first()
                u_obj.email = validate_data.get('email').lower()
                u_obj.set_password(password)
                u_obj.save()

                DossierData.objects.filter(id=validate_data.get('lid')).update(email=validate_data.get('email'))
                ManageStudentExtraDetail.objects.create(
                user=user,
                cred=password
                )
                if settings.MERITO_STATUS == "True":
                    if validate_data.get('phone') != "":
                        # API URL
                        url = settings.MERITO_BASE_URL+"/lead/v1/createOrUpdate"

                        headers = {
                            "Content-Type": "application/json",
                            "secret-key": settings.MERITO_SECRETE_KEY,
                            "access-key": settings.MERITO_ACCESS_KEY
                        }

                        payload = {
                            "email": validate_data.get('email').lower(),
                            "search_criteria": "mobile",
                            "mobile":validate_data.get('phone')
                        }
                        print("user create meritto payload...",payload)
                        try:
                            response = requests.post(url, headers=headers, json=payload)
                            print(response.status_code)
                            print(response.text)
                        except Exception as e:
                            print("API Error:", str(e))

                subject = 'Welcome to GCC School. Here are your login details.'

                message = f''
                email_from = settings.DEFAULT_FROM_EMAIL
                recipient_list = [u_obj.email, ]
                html_message = loader.render_to_string(
                    'user_login_detail_email.html',
                    {
                        'name': u_obj.first_name,
                        'candidate_id': u_obj.application_id,
                        'slot_booking': 'https://forms.gle/UQqKnCsmJzVLK6qU8',
                        'website_url': settings.WEBSITE_BASE_URL,
                        'login_url': settings.WEBSITE_BASE_URL+"/login",
                        "email": u_obj.email,
                        "password": password,               

                    }
                )

                send_mail( subject, message, email_from, recipient_list,html_message=html_message )
                
                return user
            else:
                raise serializers.ValidationError({'message':'Wrong User data','status':404,'data':[]})
        else:
            raise serializers.ValidationError({'message':'Wrong lead data','status':404,'data':[]})




class CreateUniversityStudentSerializer(serializers.ModelSerializer):
    dossier_id = serializers.CharField(max_length = 255, required=True)
    full_name = serializers.CharField(max_length = 255, required=True)
    email = serializers.EmailField(max_length = 255, required=True)
    city = serializers.CharField(max_length = 255, required=False, allow_blank=True)
    state = serializers.CharField(max_length = 255, required=False, allow_blank=True)
    country = serializers.CharField(max_length = 255, required=False, allow_blank=True)
    phone1 = serializers.CharField(max_length = 255, required=False, allow_blank=True)
    remarks = serializers.CharField(max_length = 255, required=True)
    document_status = serializers.IntegerField(required=True)
    referred_code = serializers.CharField(max_length = 255, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['dossier_id','email','full_name',"city","state","country","phone1","remarks","document_status","referred_code"]
        

    # def validate(self, data):
    #     user_count = User.objects.filter(email = data.get('email').lower()).count()
    #     if user_count > 0:
    #         raise serializers.ValidationError('Email address is already registered with Us')
        
    #     return data


    def create(self, validate_data):
        now = timezone.now()
        dat = timezone.localtime(now)
        if validate_data.get('document_status') == 2:
            user_count = User.objects.filter(email = validate_data.get('email').lower()).count()
            if user_count > 0:
                DossierData.objects.filter(id=validate_data.get("dossier_id")).update(document_status=validate_data.get('document_status'), remarks=validate_data.get('remarks'), remarks_timestamp=dat)
                raise serializers.ValidationError({'message':'Document Already Approved!','status':200,'data':[]})
            
            # waive_value = ""
            # pay_obj = Payments.objects.filter(dossier_form__email=validate_data.get('email'), status="success")
            # if pay_obj:
            #     pay_obj = pay_obj.last()
            #     waive_value = pay_obj.fee_waiver_category
            # else:
            #     pay_obj = DossierData.objects.filter(email=validate_data.get('email'))
            #     if pay_obj:
            #         pay_obj = pay_obj.last()
            #         waive_value = pay_obj.fee_waiver_category

            fee_waive = "Free of cost (FOC)"
            # refferals_code = generate_referral_code()
            refferals_code = generate_referral_code(validate_data.get('full_name'))

            password = generate_random_password(8)
            info = { "first_name": validate_data.get('full_name'), "last_name":"", 'email': validate_data.get('email').lower(), 'password': password}
            user = User.objects.create_user(**info)
            self.generated_password = password
            # assign_role(user, "Student")
            formatted_emp = str(user.id).zfill(4)
            formatted_month = str(datetime.now().date().month).zfill(2)
            formatted_year = str(datetime.now().date().year)
            generate_application_id = f"NFET-{formatted_year}-{formatted_month}{formatted_emp}"  # 000001
            user.role = User.Student
            user.email_verified = 1
            user.is_active = True
            user.country = validate_data.get('country')
            user.state = validate_data.get('state')
            user.city = validate_data.get('city')
            user.phone1 = validate_data.get('phone1')
            user.application_id = generate_application_id
            user.fee_waiver_category = fee_waive
            user.referral_code = refferals_code
            user.referred_code = validate_data.get('referred_code')
            user.save()
            num = user.id

            if validate_data.get('referred_code'):
                used_by_user = User.objects.filter(referral_code=validate_data.get('referred_code')).first()
                if used_by_user:
                    reff = ManageReferal(user=user, used_by=used_by_user, referral_code=validate_data.get('referred_code'))
                else:
                    reff = ManageReferal(user=user, used_by=None, referral_code=validate_data.get('referred_code'))
                reff.save()

            DossierData.objects.filter(email=validate_data.get('email').lower()).update(referral_code=refferals_code)
            ManageStudentExtraDetail.objects.create(
            user=user,
            cred=password
            )
            if settings.MERITO_STATUS == "True":
                
                # API URL
                url = settings.MERITO_BASE_URL+"/lead/v1/createOrUpdate"

                headers = {
                    "Content-Type": "application/json",
                    "secret-key": settings.MERITO_SECRETE_KEY,
                    "access-key": settings.MERITO_ACCESS_KEY
                }

                payload = {
                    "email": user.email,
                    "search_criteria": "email",
                    "cf_payment_status":"Complete",
                    "cf_fee_waiver_category": fee_waive,
                    "cf_refferal_code":validate_data.get('referred_code'),
                    "cf_reference_code":refferals_code
                }
                print("user create meritto payload...",payload)
                try:
                    response = requests.post(url, headers=headers, json=payload)
                    print(response.status_code)
                    print(response.text)
                except Exception as e:
                    print("API Error:", str(e))

            subject = 'Verification Successful & NFET-2026 Login Details'

            message = f''
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email, ]
            html_message = loader.render_to_string(
                'university_user_detail_email.html',
                {
                    'name': user.first_name,
                    'candidate_id': generate_application_id,
                    'slot_booking': 'https://forms.gle/UQqKnCsmJzVLK6qU8',
                    'website_url': settings.WEBSITE_BASE_URL,
                    'login_url': settings.WEBSITE_BASE_URL+"/login",
                    "email": user.email,
                    "password": password,               

                }
            )
            send_mail( subject, message, email_from, recipient_list,html_message=html_message )

            DossierData.objects.filter(id=validate_data.get("dossier_id")).update(fee_waiver_category=fee_waive, document_status=validate_data.get('document_status'),remarks=validate_data.get('remarks'),remarks_timestamp=dat)
            
            return user
        elif validate_data.get('document_status') == 3:
            
            DossierData.objects.filter(id=validate_data.get("dossier_id")).update(document_status=validate_data.get('document_status'),remarks=self.validated_data.get('remarks'),remarks_timestamp=dat)
            
            
            # subject = 'testing'

            # message = f'testing'
            # email_from = settings.DEFAULT_FROM_EMAIL
            # recipient_list = [validate_data.get('email'), ]
            # html_message = loader.render_to_string(
            #     'university_user_detail_email.html',
            #     {
            #         'name': "",
            #         'candidate_id': "",
            #         'slot_booking': 'https://forms.gle/UQqKnCsmJzVLK6qU8',
            #         'website_url': settings.WEBSITE_BASE_URL,
            #         'login_url': settings.WEBSITE_BASE_URL+"/login",
            #         "email": "",
            #         "password": "",               

            #     }
            # )
            # send_mail( subject, message, email_from, recipient_list,html_message=html_message )

            return "success"
        else:
            raise serializers.ValidationError('Invalid Request')




class StudentProfileImageUploadSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)
    class Meta:
        model = User
        fields = ['image']


        

class UserForgotPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length = 255,required=True)
    class Meta:
        model = User
        fields = ['email']

    
    def validate(self, data):
        email = data.get('email')
        if User.objects.filter(email = email).exists():
            user = User.objects.get(email = email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            
            url = settings.WEBSITE_BASE_URL+"/reset-password/?uid="+uid+'&token='+token

            subject = 'Reset Password Link'
            message = f'Hi {user.first_name} {user.last_name}, Here is the your reset password link: '+url
            
            message = f'Hi you have got a quick contact us'
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email, ]
            html_message = loader.render_to_string(
                'reset_email.html',
                {
                    'name': f'{user.first_name} {user.last_name}',
                    'verification_link': url,
                }
            )

            send_mail( subject, message, email_from, recipient_list,html_message=html_message )

            return data
        else:
            raise serializers.ValidationError('Email Not found!')





class UserResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style = { 'input_type': 'password'}, write_only = True, required = True , max_length = 20, min_length=6)
    confirm_password = serializers.CharField(style = { 'input_type': 'password'}, write_only = True, required = True, max_length = 20, min_length=6)
    uid = serializers.CharField(max_length = 255,required=True)
    token = serializers.CharField(max_length = 255,required=True)
    class Meta:
        model = User
        fields = ['password','confirm_password',"uid","token"]

    
    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        if password != confirm_password:
            raise serializers.ValidationError("Password and confirm password doesn't match")

        uid = data.get('uid')
        token = data.get('token')

        id = smart_str(urlsafe_base64_decode(uid))
        user = User.objects.filter(id=id).first()
        if user is None:
            raise serializers.ValidationError('Invalid Token')
        
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError('Invalid Token')
        user.set_password(password)
        user.save()
        
        ManageStudentExtraDetail.objects.create(
            user=user,
            cred=password
        )
        
        return data



class StudentProfileDetailSerializer(serializers.ModelSerializer):
    interview_slots_detail = serializers.SerializerMethodField("get_interview_slots_detail")
    class Meta:
        model = User
        fields = ['id','first_name','last_name', 'email','phone1','phone2','address','city','state','country','image','banner_image','pincode',"dob","application_id","interview_slots_detail"]
    
    def get_interview_slots_detail(self, obj):
        start_date = date(2026, 6, 22)
        end_date = date(2026, 7, 13)
        # Count records grouped by interview_date
        booked_slots = (
            ManageStudentInterview.objects
            .filter(interview_date__range=(start_date, end_date))
            .annotate(day=TruncDate("interview_date"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        # Convert queryset to dictionary
        count_map = {item["day"]: item["count"] for item in booked_slots}  

        # Fill missing dates with 0
        result = []
        current = start_date

        while current <= end_date:
            result.append({
                "date": current.strftime("%d-%m-%Y"),
                "count": count_map.get(current, 0)
            })
            current += timedelta(days=1)
        return result
    

    
class AdminProfileDetailSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField('get_role')
    class Meta:
        model = User
        fields = ['id','first_name','last_name', 'email','phone1','role']
    
    def get_role(get, data):
        return data.get_role_display()
