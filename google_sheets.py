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

def update_google_sheet(climber_id, bloc_id):
    try:
        creds = authenticate_google()
        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()
        
        # Translate the Bloc ID to a column letter (e.g., BLOC45 -> 'B', 'AA', etc.)
        #bloc_id_number = int(bloc_id.replace('BLOC', ''))  # Extract the number from BLOC45
        column_letter = number_to_excel_column(bloc_id)
        
        # Construct the range to update in the format "Sheet1!<column><row>"
        range_to_update = f'{SHEET}!{column_letter}{climber_id}'
        print(f'bloc_id={bloc_id} column_letter={column_letter} climber_id={climber_id}')
        
        body = {
            'values': [[1]]
        }
        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=range_to_update,
            valueInputOption='RAW',
            body=body
        ).execute()

        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

def number_to_excel_column(num):
    """Convert a number to an Excel column letter."""
    column = ""
    while num > 0:
        num -= 1
        column = chr(num % 26 + 65) + column
        num //= 26
    return column