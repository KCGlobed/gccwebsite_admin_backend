import gspread
from google.oauth2.service_account import Credentials
from django.conf import settings


def get_google_sheet():

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

    return worksheet

