import gspread
from google.oauth2.service_account import Credentials
from django.conf import settings
import time

def get_google_sheet():
    for i in range(5):
        try:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        
            credentials = Credentials.from_service_account_file(
                settings.GOOGLE_CREDENTIAL_FILE,
                scopes=scopes
            )
        
            client = gspread.authorize(credentials)
        
            spreadsheet = client.open(
                settings.GOOGLE_SHEET_NAME
            )
        
            worksheet = spreadsheet.worksheet(
                settings.GOOGLE_WORKSHEET_NAME
            )
            break
        except Exception as e:
            print("google sheet error",str(e))
            time.sleep(2)

    return worksheet


def get_google_sheet_affliate_seven():
    for i in range(5):
        try:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]

            credentials = Credentials.from_service_account_file(
                settings.GOOGLE_CREDENTIAL_FILE,
                scopes=scopes
            )

            client = gspread.authorize(credentials)

            spreadsheet = client.open(
                settings.GOOGLE_SHEET_NAME
            )

            worksheet = spreadsheet.worksheet(
                settings.GOOGLE_WORKSHEET_NAME2
            )
            break
        except Exception as e:
            print("google sheet error",str(e))
            time.sleep(2)
    return worksheet


def get_google_sheet_aeutplp():

    for i in range(5):
        try:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]

            credentials = Credentials.from_service_account_file(
                settings.GOOGLE_CREDENTIAL_FILE,
                scopes=scopes
            )

            client = gspread.authorize(credentials)

            spreadsheet = client.open(
                settings.GOOGLE_SHEET_NAME
            )

            worksheet = spreadsheet.worksheet(
                settings.GOOGLE_WORKSHEET_NAME3
            )
            break
        except Exception as e:
            print("google sheet error...")
            print(e)
            time.sleep(2)

    return worksheet

def get_google_sheet_aeuaplp():

    for i in range(5):
        try:
            # sheet = client.open_by_key(SHEET_ID)
            scopes = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]

            credentials = Credentials.from_service_account_file(
                settings.GOOGLE_CREDENTIAL_FILE,
                scopes=scopes
            )

            client = gspread.authorize(credentials)

            spreadsheet = client.open(
                settings.GOOGLE_SHEET_NAME
            )

            worksheet = spreadsheet.worksheet(
                settings.GOOGLE_WORKSHEET_NAME4
            )

            break
        except Exception as e:
            print(e)
            time.sleep(2)

    return worksheet

def get_google_sheet_affliate_eight():

    for i in range(5):
        try:
            # sheet = client.open_by_key(SHEET_ID)
            scopes = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]

            credentials = Credentials.from_service_account_file(
                settings.GOOGLE_CREDENTIAL_FILE,
                scopes=scopes
            )

            client = gspread.authorize(credentials)

            spreadsheet = client.open(
                settings.GOOGLE_SHEET_NAME
            )

            worksheet = spreadsheet.worksheet(
                settings.GOOGLE_WORKSHEET_NAME5
            )

            break
        except Exception as e:
            print(e)
            time.sleep(2)

    return worksheet


