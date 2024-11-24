from sqlite3 import DataError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID = '185s4y0PR0vvNY0wCL8cTjSOtFg2V1s3e1FqwtUZynjw'
SHEET = 'Feuille 1'

def authenticate_google():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def update_google_sheet(climber_id, bloc_id, climber_name, bloc_name):
    # Should add the bloc name and the climber name into googlesheet
    climber_row = climber_id + 1
    bloc_row = bloc_id + 1
    
    try:
        creds = authenticate_google()
        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()
        
        # Translate the Bloc ID to a column letter (e.g., 2 = 'B', 27 = 'AA', etc.)
        column_letter = number_to_excel_column(bloc_row)
        
        # Construct the range to update in the format "{SHEET}!<column><row>"
        bloc_column_range = f'{SHEET}!{column_letter}1'
        climber_name_range = f'{SHEET}!A{climber_row}'
        score_range = f'{SHEET}!{column_letter}{climber_row}'
        
        # Write bloc ID in the first row
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=bloc_column_range,
            valueInputOption='RAW',
            body={'values': [[bloc_name]]}  # Write the Bloc ID
        ).execute()

        # Write climber name in the first column
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=climber_name_range,
            valueInputOption='RAW',
            body={'values': [[climber_name]]}  # Write the climber's name
        ).execute()

        # Write score (1) in the intersecting cell
        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=score_range,
            valueInputOption='RAW',
            body={'values': [[1]]}
        ).execute()

        return result, True
    except DataError as error:
        print(f"An error occurred: {error}")
        return error, False

def number_to_excel_column(num):
    """Convert a number to an Excel column letter."""
    column = ""
    while num > 0:
        num -= 1
        column = chr(num % 26 + 65) + column
        num //= 26
    return column