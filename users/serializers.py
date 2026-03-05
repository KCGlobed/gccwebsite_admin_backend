from rest_framework import serializers
from users.models import *



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
            raise serializers.ValidationError("User is not active!")
        
        if user.email_verified == 0:
            raise serializers.ValidationError("User email is not verified!")
        
        if user:
            if not user.check_password(data.get('password')):
                raise serializers.ValidationError("Invalid Password!")
        
        return data





from django.conf import settings
from django.core.mail import send_mail
from gcc_backend.utils import *
from django.template import loader


class CreateStudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length = 255, required=True)
    email = serializers.EmailField(max_length = 255, required=True)
    city = serializers.CharField(max_length = 255, required=False, allow_blank=True)
    state = serializers.CharField(max_length = 255, required=False, allow_blank=True)
    country = serializers.CharField(max_length = 255, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email','full_name',"city","state","country"]
        

    def validate(self, data):
        user_count = User.objects.filter(email = data.get('email').lower()).count()
        if user_count > 0:
            raise serializers.ValidationError('Email address is already registered with Us')
        
        return data


    def create(self, validate_data):
        password = generate_random_password(8)
        info = { "first_name": validate_data.get('full_name'), "last_name":"", 'email': validate_data.get('email').lower(), 'password': password}
        user = User.objects.create_user(**info)
        # assign_role(user, "Student")

        user.role = User.Student
        user.email_verified = 1
        user.is_active = True
        user.country = validate_data.get('country')
        user.state = validate_data.get('state')
        user.city = validate_data.get('city')
        user.save()

        subject = 'Welcome to GCC School!'

        message = f''
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email, ]
        html_message = loader.render_to_string(
            'user_login_detail_email.html',
            {
                'name': user.first_name,
                'verification_link': 'https://gccschool.com/',
                "email": user.email,
                "password": password,               

            }
        )

        send_mail( subject, message, email_from, recipient_list,html_message=html_message )

        return user


from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator 
from django.utils.encoding import smart_str, force_bytes




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
            
            url = settings.BASE_URL+"/user/reset/?uid="+uid+'&token='+token

            subject = 'Reset Password Link'
            message = f'Hi {user.first_name} {user.last_name}, Here is the your reset password link: '+url
            
            message = f'Hi you have got a quick contact us'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            html_message = loader.render_to_string(
                'reset_email.html',
                {
                    'name': user.first_name +' '+ user.last_name,
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

        # PasswordChangeLog.objects.create(
        #     user=user
        # )
        
        return data



class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name','last_name', 'email','phone1','phone2','address','city','state','country','image','banner_image','pincode',"dob"]

