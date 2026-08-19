# # utils/google_meet.py

# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from django.conf import settings

# SCOPES = ["https://www.googleapis.com/auth/calendar"]

# def get_calendar_service():
#     credentials = service_account.Credentials.from_service_account_file(
#         settings.GOOGLE_SERVICE_ACCOUNT_FILE,
#         scopes=SCOPES,
#     )

#     return build("calendar", "v3", credentials=credentials)


# import uuid
# from datetime import datetime, timedelta

# from django.conf import settings
# # from .google_meet import get_calendar_service


# def create_google_meet(topic, start_time, duration=45, attendees=None):
#     service = get_calendar_service()

#     end_time = start_time + timedelta(minutes=duration)

#     event = {
#         "summary": topic,
#         "start": {
#             "dateTime": start_time.isoformat(),
#             "timeZone": "Asia/Kolkata",
#         },
#         "end": {
#             "dateTime": end_time.isoformat(),
#             "timeZone": "Asia/Kolkata",
#         },
#         "attendees": [{"email": email} for email in (attendees or [])],
#         "conferenceData": {
#             "createRequest": {
#                 "requestId": str(uuid.uuid4()),
#                 "conferenceSolutionKey": {
#                     "type": "hangoutsMeet"
#                 },
#             }
#         },
#     }

#     created_event = service.events().insert(
#         calendarId=settings.GOOGLE_CALENDAR_ID,
#         body=event,
#         conferenceDataVersion=1,
#         sendUpdates="all",
#     ).execute()

#     return {
#         "event_id": created_event["id"],
#         "meet_link": created_event["hangoutLink"],
#     }