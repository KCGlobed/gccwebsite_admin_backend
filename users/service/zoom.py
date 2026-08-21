import base64
import requests
from django.conf import settings

def get_zoom_access_token():
    url = "https://zoom.us/oauth/token"
    auth_str = f"{settings.ZOOM_CLIENT_ID}:{settings.ZOOM_CLIENT_SECRET}"
    encoded = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "account_credentials",
        "account_id": settings.ZOOM_ACCOUNT_ID,
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def create_zoom_meeting(topic, start_time, duration=30, timezone="Asia/Kolkata"):
    token = get_zoom_access_token()
    url = "https://api.zoom.us/v2/users/me/meetings"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "topic": topic,
        "type": 2,  # scheduled meeting
        "start_time": start_time,  # e.g. "2026-08-20T10:00:00"
        "duration": duration,
        "timezone": timezone,
        "settings": {
            "host_video": True,
            "participant_video": True,
            "join_before_host": False,
            "waiting_room": True,
        },
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()




def cancel_zoom_meeting(meeting_id, cancel_meeting_reminder=True):
    token = get_zoom_access_token()
    url = f"https://api.zoom.us/v2/meetings/{meeting_id}"
    print("ddd",url)
    headers = {
        "Authorization": f"Bearer {token}",
    }
    params = {
        "schedule_for_reminder": cancel_meeting_reminder,  # notifies host/registrants
    }
    response = requests.delete(url, headers=headers, params=params)
    if response.status_code == 204:
        return True  # success, no content returned

    response.raise_for_status()
    return False









