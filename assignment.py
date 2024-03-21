import os
import json
import base64
import sqlite3
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define the scopes for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():
    # Authentication of gmail API
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_emails(service):
    # Fetch emails from Inbox
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])
    return messages

def create_database():
    # Create SQLite database to store emails
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS emails
                 (id TEXT PRIMARY KEY, from_email TEXT, to_email TEXT, date_value TEXT,subject TEXT, body TEXT)''')
    conn.commit()
    conn.close()

def store_email(message, service):
    # Store email in SQLite database
    msg = service.users().messages().get(userId='me', id=message['id']).execute()
    headers = msg['payload']['headers']
    from_email = next((header['value'] for header in headers if header['name'] == 'From'), "")
    to_email = next((header['value'] for header in headers if header['name'] == 'Delivered-To'), "")
    date_value = next((header['value'] for header in headers if header['name'] == 'Date'), "")
    try:
        date_obj = datetime.strptime(date_value, '%a, %d %b %Y %H:%M:%S %z (%Z)')
    except:
        date_obj = datetime.strptime(date_value, '%a, %d %b %Y %H:%M:%S %z')
    date_of_email = date_obj.strftime('%Y-%m-%d')
    subject = next((header['value'] for header in headers if header['name'] == 'Subject'), "")
    try:
        body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
    except:
        body = msg['snippet']
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO emails (id, from_email,to_email,date_value,subject, body) VALUES (?, ?, ?, ?, ?, ?)", (message['id'], from_email, to_email,date_of_email,subject, body))
    conn.commit()
    conn.close()


def main():
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)
    
    create_database()

    emails = get_emails(service)
    for email in emails:
        try:
            store_email(email, service)
        except:
            pass

if __name__ == '__main__':
    main()
