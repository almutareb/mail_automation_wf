# In Google Cloud console -> API & Services -> Library -> search for Gmail API -> ensure Gmail API is enabled
# In Google Cloud console -> API & Services -> Credentials -> create Auth02 credential -> download json and save as credentials.json
# In Google Cloud console -> API & Services -> OAuth consent screen -> Test users -> insert the email ID of the user 

import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from email.utils import parsedate_to_datetime
import base64
from pathlib import Path
import json


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_service(credentials_json:str='credentials.json') -> Resource:
    """ Creates a Gmail authentication flow """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file=credentials_json, 
                                                             scopes=SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service  


def get_messages(service:Resource, user_id='me', label_ids=['INBOX']) -> list | None:
    try:
        response = service.users().messages().list(userId=user_id, labelIds=label_ids).execute()
        messages = response.get('messages', [])
        return messages
    except Exception as e:
        print(f'An error occurred: {e}')
        return None


def get_email_body(message_payload:dict) -> str | None:
    """ Returns the email body as a string """

    if 'parts' in message_payload:
        for part in message_payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif 'parts' in part:
                # Recursively check nested parts
                body = get_email_body(part)
                if body:
                    return body
    elif 'body' in message_payload:
        if 'data' in message_payload['body']:
            return base64.urlsafe_b64decode(message_payload['body']['data']).decode('utf-8')
    
    # If no text/plain part is found
    return None


def get_attachment(message_payload:dict, 
                   service:Resource, 
                   user_id='me', 
                   msg_id=None, 
                   attachment_dir:str='Attachments') -> list[str]:
    """ Download the attachment from an email to disk """
    attachments = []
    try:
        if 'parts' in message_payload:
            for part in message_payload['parts']:
                if part.get('filename'):
                    attachment_name = part['filename']
                    if 'data' in part['body']:
                        file_data = base64.urlsafe_b64decode(part['body']['data'].encode('UTF-8'))
                    elif 'attachmentId' in part['body']:
                        attachment = service.users().messages().attachments().get(userId=user_id, 
                                                                                messageId=msg_id, 
                                                                                id=part['body']['attachmentId']
                                                                                ).execute()
                        file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                    else:
                        file_data = None
                        print(f'No file data')
                    
                    if file_data:
                        attachment_save_name = f'{msg_id}_{attachment_name}'
                        # Actual path to disk
                        attachment_save_path = (Path.cwd()/attachment_dir/attachment_save_name).as_posix()
                        # Relative path to dict/json
                        project_dir = Path.cwd().parent.parent.name
                        project_dir_idx = Path.cwd().parts.index(project_dir)
                        relative_path = '/'.join(Path.cwd().parts[project_dir_idx:])
                        attachments.append(f"{relative_path}/{attachment_dir}/{attachment_save_name}")

                        if (Path.cwd()/attachment_dir/attachment_save_name).exists():
                            print("File already exists -> not saving")
                        else:
                            with open(file=attachment_save_path, mode='wb') as f:
                                f.write(file_data)
                    

    except Exception as error:
        print(f'An error occurred: {error}')

    return attachments


def get_message_details(service, user_id='me', msg_id=None) -> dict | None:
    """ Returns the message details as a dict """

    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
        
        headers = message['payload']['headers']

               
        subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No subject')
        from_email = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'No sender')
        to_email = next((header['value'] for header in headers if header['name'].lower() == 'to'), 'No recipient')
        date = next((header['value'] for header in headers if header['name'].lower() == 'date'), 'No date')
        body = get_email_body(message['payload'])
        attachments = get_attachment(message_payload=message['payload'], 
                                          service=service, 
                                          user_id=user_id, 
                                          msg_id=msg_id)

         # Convert date string to datetime object
        try:
            from email.utils import parsedate_to_datetime
            date_time = parsedate_to_datetime(date)
        except:
            date_time = date  # Keep as string if parsing fails
        return {
                'id':msg_id,
                'from':from_email,
                'to': to_email,
                'subject': subject,
                'date': date_time,
                'body':body,
                'attachments': attachments
            }
    
    except Exception as e:
        print(f'An error occurred: {e}')
        return None


def add_email_to_json(emails_json_file:str, email_data:dict) -> None:
    """ Adds the email details to a json file """
    
    assert Path(emails_json_file).is_file(), "File does not exist"

    with open(file=emails_json_file, mode='r') as file:
        emails_json = json.load(file)

    entry_id = email_data['id']

    if entry_id in [email['entry_id'] for email in emails_json]:
        print(f"Email with entry ID: {entry_id} already exists")
        return
    
    data_to_add = {
        'entry_id':email_data['id'],
        'from':email_data['from'],
        'to':email_data['to'],
        'subject':email_data['subject'],
        'body':email_data['body'],
        'received_time':email_data['date'].strftime("%d-%m-%Y- %H:%M:%S"),
        'attachments':email_data['attachments']
    }

    emails_json.append(data_to_add)

    with open(file=emails_json_file, mode='w', encoding='utf-8') as json_file:
        json.dump(obj=emails_json, fp=json_file, ensure_ascii=False, indent=4)


def main():
    service = get_service()
    messages = get_messages(service=service)
    if not messages:
        print("No messages")
        return
    for message in messages:
        email_data = get_message_details(service=service, msg_id=message['id'])
        # Condition to save the email
        if 'Test_App_Email_1234' in email_data['subject']:
            add_email_to_json(emails_json_file="emails.json", email_data=email_data)


if __name__ == "__main__":
    main()
    