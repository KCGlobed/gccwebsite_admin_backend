from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
import random
import string

import time
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

    send_mail( subject, message, email_from, recipient_list,html_message=html_message)

    print("end calling, mail sent")


from django.core.mail import EmailMultiAlternatives
def send_email_async_multiple(subject, message, email_from, recipient_list, html_message, cc_list=None):
    print("start calling")

    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=email_from,
        to=recipient_list,
        cc=cc_list or [],
    )

    email.attach_alternative(html_message, "text/html")
    email.send()

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


from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+
from career.models import DossierData
from users.service import zoom
# class CreateZoommMeetingAPIView(APIView):

def send_email_invite(std_id):
    std = std_id
    obj = DossierData.objects.get(id=std)
    topic = "GCC School | Admission Counselling Session"
    # start_time = request.data.get("start_time")
    interview_date = obj.interview_date      # date object
    slot_time = obj.slot_time                # "09:45 AM"

    # Combine date + time in IST
    dt_ist = datetime.strptime(
        f"{interview_date} {slot_time}",
        "%Y-%m-%d %I:%M %p"
    ).replace(tzinfo=ZoneInfo("Asia/Kolkata"))

    # Convert to UTC ISO format
    zoom_start_time = dt_ist.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")

    print(zoom_start_time)
    duration = 45
    meeting = zoom.create_zoom_meeting(
        topic=topic,
        start_time=zoom_start_time,
        duration=duration
    )
    join_link = meeting["join_url"]
    admin_link = meeting["start_url"]
    meeting_id = meeting["id"]
    password = meeting["password"]
    send_zoom_invite_email(std,join_link,admin_link,meeting_id,password)

    return "success"


def create_affliate_seven_services_async(instance, src_type, validated_data):
    print("affliate seven call...",instance, src_type)
    trigger = False
    if settings.MERITO_STATUS == "True":
        if src_type == 15:
            m_source = "gccaffiliateSeven"
        elif src_type == 20:
            m_source = "gccealpCampaign"
        elif src_type == 21:
            m_source = "gcccpalpCampaign"
        elif src_type == 22:
            m_source = "gccealpRudrapur"
        elif src_type == 23:
            m_source = "gccaffliateEight"
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
            if not DossierData.objects.filter(phone=instance.phone, source=src_type).exclude(id=instance.id).exists():
                trigger = True
                try:
                    sheet = get_google_sheet_affliate_seven()
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
            if not DossierData.objects.filter(phone=instance.phone, source=src_type).exclude(id=instance.id).exists():
                try:
                    sheet = get_google_sheet_aeutplp()
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
            if not DossierData.objects.filter(phone=instance.phone, source=src_type).exclude(id=instance.id).exists():
                try:
                    sheet = get_google_sheet_aeuaplp()
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
        elif src_type == 23:
            if not DossierData.objects.filter(phone=instance.phone, source=src_type).exclude(id=instance.id).exists():
                try:
                    print("start excel")
                    if instance.speak_with == 1:
                        meet = "Kamal Chhabra"
                    elif instance.speak_with == 2:
                        meet = "Nitish Khatri"
                    else:
                        meet = "N/A"
                    sheet = get_google_sheet_affliate_eight()
                    
                    local_time = timezone.localtime(instance.created_at)
                    create_times = local_time.strftime("%Y-%m-%d %H:%M:%S")

                    session_str_date = instance.interview_date.strftime("%Y-%m-%d")
                    row = [
                        instance.full_name,
                        instance.email,
                        instance.phone,
                        instance.child_full_name,
                        instance.child_email,
                        instance.child_phone,
                        instance.degree,
                        instance.age_range,
                        instance.degree_stage,
                        meet,
                        session_str_date,
                        instance.slot_time,
                        create_times
                    ]
                    print("data inster",row)
                    sheet.append_row(row)
                    print("completed")
                except Exception as e:
                    print("google sheet error", str(e))

    if instance.source == 23:
        send_email_invite(instance.id)
    else:
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

        if settings.EXCEL_INPUT == "True":
            if trigger:
                time.sleep(30)
                send_interview_trigger_email(instance)

    return "success"





def update_affliate_seven_services_async(lobj, src_type):
    if settings.EXCEL_INPUT == "True":
        if src_type == 15:
            try:
                sheet = get_google_sheet_affliate_seven()
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
                    sheet.update(f"K{row_number}:L{row_number}", [row_data])
                    print(f"Row {row_number} updated successfully")

                    print("row updated successfully")

                else:
                    print("row not found, new row inserted")
            except Exception as e:
                print("google sheet error", str(e))
        elif src_type == 20:
            try:
                sheet = get_google_sheet_aeutplp()
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



def send_interview_trigger_email(student):

    obj = DossierData.objects.get(id=student.id)

    subject = f"New Lead Received"
    slot = obj.interview_date
    if not obj.interview_date:
        slot = "N/A"
    html_message = render_to_string(
        "emails/dossier_trigger.html",
        {
            "full_name": obj.full_name,
            "email": obj.email,
            "phone": obj.phone,
            "city": obj.city,
            "state": obj.state,
            "degree": obj.degree,
            "age_range": obj.age_range,
            "degree_stage": obj.degree_stage,
            "fund_mode": obj.fund_mode,
            "interview_slot": slot
        },
    )

    send_email_async_multiple(subject, "", settings.DEFAULT_FROM_EMAIL, ['vironika.takkar@kcglobed.com'], html_message, cc_list=['info@kcglobed.com','akshay.jangra@gccschool.com'],)

    return "success"




def create_affliate_six_services_async(instance, src_type):
    if settings.EXCEL_INPUT == "True":
        if src_type == 14:
            if not DossierData.objects.filter(phone=instance.phone, source=src_type).exclude(id=instance.id).exists():
                print("valida data")
                try:
                    sheet = get_google_sheet()
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
                    sheet.append_row(row)
                    print("completed")
                except Exception as e:
                    print("google sheet error", str(e))

    return "success"

from datetime import datetime

def ordinal(n):
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"





def send_zoom_invite_email(student, zoom_link, admin_link, meeting_id, password):

    obj = DossierData.objects.get(id=student)
    send_to = obj.email
    support_email = "placement.support@kcglobed.com"
    if obj.speak_with == 1:
        speaker = "Kamal Chhabra"
        des = "Founder & CEO - KC GlobEd & GCC School"
        send_admin = "kamal.chhabra@kcglobed.com"
        # send_admin = "vishal.dubey@kcglobed.com"
    else:
        speaker = "Nitish Khatri"
        des = "Vice President, KC GlobEd & GCC School"
        send_admin = "nitish.khatri@kcglobed.com"
        # send_admin = "vishal.dubey@kcglobed.com"

    subject = f"Session With {speaker}"

    # Values for email template
    session_day = obj.interview_date.strftime("%A")  # Sunday
    session_date = (
            f"{ordinal(obj.interview_date.day)} "
            f"{obj.interview_date.strftime('%B %Y')}"
        )  # 16th August 2026

    html_message = render_to_string(
        "zoom_invite.html",
        {
            "parent_name": obj.full_name,
            "child_name": obj.child_full_name,
            "Speaker_name": speaker,
            "Speaker_designation":des,
            "session_day": session_day,
            "session_date": session_date,
            "session_time": obj.slot_time,
            "child_qualification": obj.degree,
            "lead_id": obj.id,
            "zoom_link": zoom_link,
            "meeting_id": meeting_id,
            "password": password,
            "calendar_google_url": "",
            "calendar_ics_url": "",
            "reschedule_url": "",
            "whatsapp_url": "https://web.whatsapp.com/send?phone=918796880189",
            "support_phone": "8796880189",
            "support_email": "info@gccschool.com",
            "header_image_url":"https://storage.googleapis.com/gcc_prod_static_files_backend/static/images/gcc_dlf_logo.jpg"
        },
    )
    subject_admin = f"New Interview Scheduled | {obj.child_full_name} | {obj.degree}"
    html_msg = render_to_string(
            "admin_invite.html",
            {
                "parent_name": obj.full_name,
                "parent_email": obj.email,
                "parent_phone": obj.phone,
                "child_name": obj.child_full_name,
                "Speaker_name": speaker,
                "Speaker_designation":des,
                "session_day": session_day,
                "session_date": session_date,
                "session_time": obj.slot_time,
                "child_qualification": obj.degree,
                "lead_id": obj.id,
                "admin_link": admin_link,
                "calendar_google_url": "",
                "calendar_ics_url": "",
                "reschedule_url": "",
                "whatsapp_url": "https://web.whatsapp.com/send?phone=918796880189",
                "support_phone": "8796880189",
                "support_email": "info@gccschool.com",
                "header_image_url":"https://storage.googleapis.com/gcc_prod_static_files_backend/static/images/gcc_dlf_logo.jpg"
            },
        )
    send_email_async_multiple(subject, "", settings.DEFAULT_FROM_EMAIL, [send_to, support_email], html_message, cc_list=['akshay.jangra@gccschool.com','vironika.takkar@kcglobed.com','kamal.chhabra@kcglobed.com','nitish.khatri@kcglobed.com'])
    send_email_async_multiple(subject_admin, "", settings.DEFAULT_FROM_EMAIL, [send_admin, support_email], html_msg, cc_list=['akshay.jangra@gccschool.com','vironika.takkar@kcglobed.com','kamal.chhabra@kcglobed.com','nitish.khatri@kcglobed.com'])

    return "success"
