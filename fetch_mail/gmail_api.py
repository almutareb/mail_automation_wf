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
from email.mime.text import MIMEText



SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']


def get_service(credentials_json: str = 'credentials.json', token_file:str = 'token.pickle') -> Resource:
    """ Creates a Gmail authentication flow """
    creds = None
    if os.path.exists(token_file):
        with open(file=token_file, mode='rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file=credentials_json,
                                                             scopes=SCOPES)
            creds = flow.run_local_server(port=0)
        with open(file=token_file, mode='wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service


def get_messages(service: Resource, user_id='me', label_ids=['INBOX']) -> list | None:
    try:
        response = service.users().messages().list(
            userId=user_id, labelIds=label_ids).execute()
        messages = response.get('messages', [])
        return messages
    except Exception as e:
        print(f'An error occurred: {e}')
        return None


def get_email_body(message_payload: dict) -> str | None:
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


def has_attachments(message_payload:dict) -> bool:
    """ Returns True if there is an attachment
    """
    if 'parts' in message_payload:
        for part in message_payload['parts']:
            if part.get('filename'):
                return True
            if 'parts' in part:
                if has_attachments(part):
                    return True
    return False


def get_attachment(message_payload: dict,
                   service: Resource,
                   user_id='me',
                   msg_id=None,
                   attachment_dir: str = None) -> list[str]:
    """ Download the attachment from an email to disk """
    attachments = []
    
    try:
        if 'parts' in message_payload:
            for part in message_payload['parts']:
                if part.get('filename'):

                    # Create a folder with the name of the message ID    
                    project_dir = Path(__file__).parent.parent.resolve()

                    attachment_folder = project_dir/ attachment_dir / str(msg_id)
                    attachment_folder.mkdir(parents=True, exist_ok=True)

                    attachment_name = part['filename']
                    if 'data' in part['body']:
                        file_data = base64.urlsafe_b64decode(
                            part['body']['data'].encode('UTF-8'))
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
                        # attachment_save_name = f'{msg_id}_{attachment_name}'
                        # # Actual path to disk
                        # attachment_save_path = (Path.cwd()/attachment_dir/attachment_save_name).as_posix()
                        # # Relative path to dict/json
                        # project_dir = Path.cwd().parent.parent.name
                        # project_dir_idx = Path.cwd().parts.index(project_dir)
                        # relative_path = '/'.join(Path.cwd().parts[project_dir_idx:])
                        # attachments.append(f"{relative_path}/{attachment_dir}/{attachment_save_name}")
                        
                        # if (Path.cwd()/attachment_dir/attachment_folder/attachment_name).exists():
                        #     print("Attachment already exists -> not saving it again")
                        # else:
                        #     with open(file=attachment_save_path, mode='wb') as f:
                        #         f.write(file_data)

                        attachments.append(attachment_name)

                        
                        attachment_save_path = attachment_folder/attachment_name
                        if attachment_save_path.exists():
                            print("Attachment already exists -> not saving it again")
                        else:
                            with open(file=attachment_save_path.as_posix(), mode='wb') as f:
                                f.write(file_data)

    except Exception as error:
        print(f'An error occurred: {error}')

    return attachments


def get_message_details(service:Resource, user_id='me', msg_id=None) -> dict | None:
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
                                     msg_id=msg_id,
                                     attachment_dir=attachment_dir)

        # Convert date string to datetime object
        try:
            date_time = parsedate_to_datetime(date)
        except:
            date_time = date  # Keep as string if parsing fails
        return {
            'id': msg_id,
            'from': from_email,
            'to': to_email,
            'subject': subject,
            'date': date_time.strftime("%d-%m-%Y- %H:%M:%S"),
            'body': body,
            'attachments': attachments
        }

    except Exception as e:
        print(f'An error occurred: {e}')
        return None


def add_email_to_json(emails_json_file: str, email_data: dict) -> None:
    """ Adds the email details to a json file """

    assert Path(emails_json_file).is_file(), "File does not exist"

    with open(file=emails_json_file, mode='r') as file:
        emails_json = json.load(file)

    entry_id = email_data['id']

    if entry_id in [email['entry_id'] for email in emails_json]:
        print(f"Email with entry ID: {entry_id} already exists")
        return

    data_to_add = {
        'message_id': email_data['id'],
        'from': email_data['from'],
        'to': email_data['to'],
        'subject': email_data['subject'],
        'body': email_data['body'],
        'received_time': email_data['date'].strftime("%d-%m-%Y- %H:%M:%S"),
        'attachments': email_data['attachments']
    }

    emails_json.append(data_to_add)

    with open(file=emails_json_file, mode='w', encoding='utf-8') as json_file:
        json.dump(obj=emails_json, fp=json_file, ensure_ascii=False, indent=4)


def add_email_json_dir(email_data: dict, json_dir_loc:str, status_file:str) -> None:
    """
    Saves email data to json file with the message ID as file name

    Args:
        email_data (dict): dictionary containing the email data
    """
    message_id = email_data['id']

    file_path = Path(json_dir_loc)/f"{message_id}.json"
    if file_path.exists():
        print(f"Message with id: {message_id} already exisit -> not saving it again")
        return 
     
    data_to_add = {
    'message_id': email_data['id'],
    'from': email_data['from'],
    'to': email_data['to'],
    'subject': email_data['subject'],
    'body': email_data['body'],
    'received_time': email_data['date'].strftime("%d-%m-%Y- %H:%M:%S"),
    'attachments': email_data['attachments']
    }



def get_emails(service: Resource,
               subject_filter:str = "Test_App_Email_1234",
               attachment_dir:str = None,
               emails_json_dir:str = None,
               status_file:str = None) -> list:
    """
    Downloads emails to json and attachments to file and labels emails and downloaded

    Args:
        service (Resource) : Gmail authentication flow resource
        subject_filter (str) : The text in the subject that would  

    Returns:
        list: list of message ids of emails that have been downloaded
    """

    message_ids = []

    messages = get_messages(service=service)
    if not messages:
        print("No messages")
        return
    for message in messages:
        email_data = get_message_details(service=service, msg_id=message['id'])
        # Condition to save the email
        if 'Test_App_Email_1234' in email_data['subject']:
            add_email_to_json(emails_json_file="emails.json", email_data=email_data)


def create_message(sender:str, to:str, subject:str, message_text:str) -> dict:
    """ Creates an email message """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
    return {'raw': raw_message.decode("utf-8")}


def send_message(service:Resource, user_id='me', message:dict=None):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print('Message Id: %s' % message['id'])
        return message
    except Exception as e:
        print('An error occurred: %s' % e)
        return None


if __name__ == "__main__":
    # main()
    service = get_service()
    msg = create_message(sender='me', to='karan@artiquare.com', subject='Test sending email', message_text="Thank you for getting in touch")
    message = send_message(service=service, message=msg)
    print(f"{type(message) = }")
    print(f"{message = }")

