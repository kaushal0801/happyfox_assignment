import os
import json
import base64
import sqlite3
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build



def get_field_to_search_name(name):
    import pdb;pdb.set_trace()
    if name == "From":
        return "from_email"
    elif name == "To":
        return "to_email"
    elif name == "Subject":
        return "subject"
    elif name == "Date received":
        return "date_value"
    else:
        return "body"

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

def get_emails_satisfying_conditions(c, conditions,top_filter_value):
    """Retrieve emails satisfying all conditions."""
    import pdb;pdb.set_trace()
    emails = []
    for condition in conditions:
        predicate = condition.get('predicate')
        name = condition.get('name')
        filter_to_search  = get_field_to_search_name(name)

        if predicate == 'contains':
            value = condition.get('value')
            c.execute("""SELECT * FROM emails WHERE %s LIKE %s"""%(filter_to_search,"'%s'" % str("%"+value+"%")))
            current_emails  = c.fetchall()
            if emails:
                emails = current_emails
            else:
                if top_filter_value == "All":
                    emails = [email for email in emails if email in current_emails]
                else:
                    emails = list(set(current_emails+emails))

        if predicate == 'equals':
            value = condition.get('value')
            c.execute("""SELECT * FROM emails WHERE %s = %s"""%(filter_to_search,value,))
            current_emails  = c.fetchall()
            if emails:
                emails = current_emails
            else:
                if top_filter_value == "All":
                    emails = [email for email in emails if email in current_emails]
                else:
                    emails = list(set(current_emails+emails))

        if predicate == 'not equals':
            value = condition.get('value')
            c.execute("""SELECT * FROM emails WHERE %s != %s"""%(filter_to_search,value,))
            current_emails  = c.fetchall()
            if emails:
                emails = current_emails
            else:
                if top_filter_value == "All":
                    emails = [email for email in emails if email in current_emails]
                else:
                    emails = list(set(current_emails+emails))

        if predicate == 'is less than':
            value = condition.get('value')
            c.execute("""SELECT * FROM emails WHERE %s < DATETIME('now', '-%s day')"""%(filter_to_search,int(value),))
            current_emails  = c.fetchall()
            if emails:
                emails = current_emails
            else:
                if top_filter_value == "All":
                    emails = [email for email in emails if email in current_emails]
                else:
                    emails = list(set(current_emails+emails))

    return emails if emails else []

def execute_action(service, action, message_id):
    import pdb;pdb.set_trace()
    """Execute action on email."""
    action_name = action.get("name")
    
    label = action.get("label")
    if action_name == 'Move Message':
        # Assuming value is 'Inbox', for other value we can write further functions based on value
        value = action.get("value") 
        move_to_inbox(service, message_id)
    if not action_name:
        if label == "Mark as read":
            mark_as_read(service, message_id)
        elif label == "mark as unread":
            mark_as_unread(service, message_id)


def move_to_inbox(service, message_id):
    import pdb;pdb.set_trace()
    """Move an email to the Inbox."""
    body = {'addLabelIds': ['INBOX']}
    service.users().messages().modify(userId='me', id=message_id, body=body).execute()

def mark_as_read(service, message_id):
    import pdb;pdb.set_trace()
    """Mark an email as read."""
    body = {'removeLabelIds': ['UNREAD']}
    service.users().messages().modify(userId='me', id=message_id, body=body).execute()

def mark_as_unread(service, message_id):
    import pdb;pdb.set_trace()
    body = {'removeLabelIds': ['READ']}
    service.users().messages().modify(userId='me', id=message_id, body=body).execute()


def process_emails(rules,service):
    import pdb;pdb.set_trace()
    """Process emails based on rules."""
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    for rule in rules:
        top_filter_value = rule.get('predicate',"All")
        conditions = rule.get('criteria', [])
        actions = rule.get('action', [])
        emails_based_on_conditions = get_emails_satisfying_conditions(c,conditions,top_filter_value)
        for email in emails_based_on_conditions:
            for action in actions:
                execute_action(service, action, email[0])
    
    conn.close()

def main():
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)
    import pdb;pdb.set_trace()
    with open('rules.json', 'r') as f:
        rules = json.load(f)
    
    process_emails(rules,service)

if __name__ == '__main__':
    main()
