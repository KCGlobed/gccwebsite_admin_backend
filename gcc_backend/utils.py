from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
import random
import string
from datetime import datetime


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def create_response(success, message, data=None, status_code=status.HTTP_200_OK):
    response_data = {
        "success": success,
        "status": str(status_code),
        "message": message,
        "data": data if data is not None else {}
    }
   
    return Response(response_data, status=status_code)
 
def success_response(message, data=None, status_code=status.HTTP_200_OK):
    return create_response(True, message, data, status_code)
 
def error_response(message, data=None, status_code=status.HTTP_400_BAD_REQUEST):
    return create_response(False, message, data, status_code)



def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return (
        x_forwarded_for.split(",")[0]
        if x_forwarded_for
        else request.META.get("REMOTE_ADDR")
    )



def generate_random_password(length=8):
    letters = string.ascii_letters 
    digits = string.digits       
    special_characters = '@#$%&*'
    password = [
        random.choice(special_characters),  
        random.choice(letters),             
        random.choice(digits)
    ]
    all_characters = letters + digits + special_characters
    password += random.choices(all_characters, k=length - 3)
    random.shuffle(password)
    return ''.join(password)

from django.core.mail import send_mail
from django.conf import settings
from django.template import loader

def send_email_async(subject, message, email_from, recipient_list, html_message):
    print("start calling")
    subject = subject
    message = message
    email_from = email_from
    recipient_list = recipient_list
    html_message = html_message

    send_mail( subject, message, email_from, recipient_list,html_message=html_message )

    print("end calling")

from users.models import User
def get_lower_reporting(user):
    data = []
    data.append(user)
    def fetch_all(id):
        users_list = User.objects.filter(reporting_to=id)
        for i in users_list:
            data.append(i.id)
            fetch_all(i.id)
    fetch_all(user)                    
    return data

def get_upper_reporting(user):
    data = []
    # data.append(user)
    obj = User.objects.filter(id=user).first()
    def fetch_all(obj):
        users_all = User.objects.filter(id=obj.reporting_to).first()
        data.append(users_all.id)
        print("add",data)
        if users_all.reporting_to != "0":
            fetch_all(users_all)
    fetch_all(obj)                    
    return data


def parse_date(date_str):
    parsed_date = date_str
    type(parsed_date)
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        print("gg", parsed_date)
    except ValueError as e:
        print(str(e), parsed_date)
        # day is out of range for month
    print("data...", parsed_date)
    print(type(parsed_date))
    return parsed_date
