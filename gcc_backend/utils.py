from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
import random
import string

from django.core.mail import send_mail
from django.conf import settings
from django.template import loader
from datetime import datetime

import requests
from django.utils import timezone
from utils.google_sheet import *
from career.models import *
from users.models import User
from students.models import StudentProfile, ManageStudentInterview
from users.serializers import StudentProfileDetailSerializer


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


def send_email_async(subject, message, email_from, recipient_list, html_message):
    print("start calling")
    subject = subject
    message = message
    email_from = email_from
    recipient_list = recipient_list
    html_message = html_message

    send_mail( subject, message, email_from, recipient_list,html_message=html_message )

    print("end calling, mail sent")




def parse_date(date_str):
    parsed_date = date_str
    type(parsed_date)
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        print("gg", parsed_date)
    except ValueError as e:
        print(str(e), parsed_date)
        # day is out of range for month
    return parsed_date




def create_affliate_seven_services_async(instance, src_type, validated_data):
    print("affliate seven call...",instance, src_type)
    if settings.MERITO_STATUS == "True":
        if src_type == 15:
            m_source = "gccaffiliateSeven"
        elif src_type == 20:
            m_source = "gccealpCampaign"
        elif src_type == 21:
            m_source = "gcccpalpCampaign"
        else:
            m_source = "gcc"
        print("m_source...",m_source)
        # API URL
        url = settings.MERITO_BASE_URL+"/lead/v1/createOrUpdate"

        headers = {
            "Content-Type": "application/json",
            "secret-key": settings.MERITO_SECRETE_KEY,
            "access-key": settings.MERITO_ACCESS_KEY
        }

        payload = {
            "name": instance.full_name,
            "email": instance.email,
            "mobile": instance.phone,
            "city": instance.city,
            "state": instance.state,
            "search_criteria": "email",
            "source":m_source,
            "cf_source":m_source,
            "cf_payment_status":"Complete",
            "cf_fee_waiver_category":"Free of cost (FOC)"
        }
        try:
            print("mer..",payload)
            response = requests.post(url, headers=headers, json=payload)
            print(response.status_code)
            print(response.text)
            DossierLog.objects.create(dossier=instance, message=response.text, status=int(response.status_code), activity="creating", datas=validated_data)
        except Exception as e:
            print("API Error:", str(e))

    if settings.EXCEL_INPUT == "True":
        if src_type == 15:
            print("sheet enter")
            if not DossierData.objects.filter(phone=instance.phone, source=src_type).exclude(id=instance.id).exists():
                print("valida data")
                try:
                    sheet = get_google_sheet_affliate_seven()
                    print("open sheet...",sheet)
                    local_time = timezone.localtime(instance.created_at)
                    create_times = local_time.strftime("%Y-%m-%d %H:%M:%S")
                    row = [
                        instance.full_name,
                        instance.email,
                        instance.phone,
                        instance.city,
                        instance.state,
                        instance.degree,
                        instance.age_range,
                        instance.degree_stage,
                        instance.fund_mode,
                        instance.attend_from,
                        "No",
                        "",
                        create_times
                    ]
                    print("data inster",row)
                    sheet.append_row(row)
                    print("completed")
                except Exception as e:
                    print("google sheet error", str(e))

        elif src_type == 20:
            print("sheet enter")
            if not DossierData.objects.filter(phone=instance.phone, source=src_type).exclude(id=instance.id).exists():
                print("valida data")
                try:
                    sheet = get_google_sheet_aeutplp()
                    print("open sheet...",sheet)
                    local_time = timezone.localtime(instance.created_at)
                    create_times = local_time.strftime("%Y-%m-%d %H:%M:%S")
                    row = [
                        instance.full_name,
                        instance.email,
                        instance.phone,
                        instance.city,
                        instance.state,
                        instance.degree,
                        instance.age_range,
                        instance.degree_stage,
                        instance.fund_mode,
                        instance.attend_from,
                        "No",
                        "",
                        create_times
                    ]
                    print("data inster",row)
                    sheet.append_row(row)
                    print("completed")
                except Exception as e:
                    print("google sheet error", str(e))
        elif src_type == 21:
            print("sheet enter")
            if not DossierData.objects.filter(phone=instance.phone, source=src_type).exclude(id=instance.id).exists():
                print("valida data")
                try:
                    sheet = get_google_sheet_aeuaplp()
                    print("open sheet...",sheet)
                    local_time = timezone.localtime(instance.created_at)
                    create_times = local_time.strftime("%Y-%m-%d %H:%M:%S")
                    row = [
                        instance.full_name,
                        instance.email,
                        instance.phone,
                        instance.city,
                        instance.state,
                        instance.degree,
                        instance.age_range,
                        instance.degree_stage,
                        instance.fund_mode,
                        instance.attend_from,
                        "No",
                        "",
                        create_times
                    ]
                    print("data inster",row)
                    sheet.append_row(row)
                    print("completed")
                except Exception as e:
                    print("google sheet error", str(e))
        else:
            pass

    url = settings.CSRF_TRUSTED_ORIGINS[0]+"/api/users/create_student/"

    payload = {
        "full_name": instance.full_name,
        "email": instance.email,
        "phone1": instance.phone
    }
    try:
        print("user....",payload)
        response = requests.post(url, json=payload)
        print(response.status_code)
        print(response.text)
        User.objects.filter(email=instance.email).update(city=instance.city, state=instance.state, fee_waiver_category="Free of cost (FOC)")
        # DossierLog.objects.create(dossier=instance, message=response.text, status=int(response.status_code), activity="creating", datas=validated_data)
    except Exception as e:
        print("API Error:", str(e))

    return "success"





def update_affliate_seven_services_async(lobj, src_type):
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
        elif src_type == 20:
            print("sheet enter")
            try:
                sheet = get_google_sheet_aeutplp()
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
        elif src_type == 21:
            print("sheet enter")
            try:
                sheet = get_google_sheet_aeuaplp()
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
        else:
            pass
    send_interview_reserved_email(lobj)
    return "success"



from django.template.loader import render_to_string
from django.conf import settings
import threading


def send_interview_reserved_email(student):
    subject = f"Congratulations, {student.full_name} — Your Interview Seat is Reserved"

    html_message = render_to_string(
        "emails/interview_reserved.html",
        {
            "first_name": student.full_name,
            "phone": student.phone,
            "interview_slot": student.interview_date,
        },
    )

    threading.Thread(
        target=send_email_async,
        args=(
            subject,
            "",
            settings.DEFAULT_FROM_EMAIL,
            [student.email],
            html_message,
        ),
    ).start()









def create_affliate_six_services_async(instance, src_type):
    if settings.EXCEL_INPUT == "True":
        if src_type == 14:
            print("sheet enter")
            if not DossierData.objects.filter(phone=instance.phone, source=src_type).exclude(id=instance.id).exists():
                print("valida data")
                try:
                    sheet = get_google_sheet()
                    print("open sheet...",sheet)
                    local_time = timezone.localtime(instance.created_at)
                    create_times = local_time.strftime("%Y-%m-%d %H:%M:%S")
                    row = [
                        instance.full_name,
                        instance.email,
                        instance.phone,
                        instance.city,
                        instance.state,
                        instance.fbc_id,
                        instance.utm_source,
                        instance.utm_medium,
                        instance.utm_content,
                        instance.utm_campaign,
                        instance.campaign_id,
                        instance.utm_adname,
                        instance.adset_id,
                        instance.fbclid,
                        instance.ad_source,
                        instance.ad_id,
                        instance.fee_waiver_category,
                        create_times
                    ]
                    print("data inster",row)
                    sheet.append_row(row)
                    print("completed")
                except Exception as e:
                    print("google sheet error", str(e))

    return "success"



