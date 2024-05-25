from pathlib import Path
from pathlib import Path
from datetime import datetime
import uuid
import json
import os
import win32com.client
from dotenv import load_dotenv

load_dotenv()  

# ====================================================================
# Note: For Windows systems running Outlook desktop email client only
# ====================================================================

def save_attachments(attachments:list,
                     email_uuid:str,
                     attachment_dir:Path=None) -> list[str]:
    """ Saves the attachments to a folder """
    
    attachment_paths = []
    
    # If attachment_dir == None, then creates an Attachments folder in cwd 
    if attachment_dir is None:
        attachment_dir = Path.cwd()/"Attachments"
        if not attachment_dir.exists():
            attachment_dir.mkdir(parents=True, exist_ok=True)
        
    for attachment in attachments:
        attachment_name = attachment.FileName
        unique_attachment_name = f"{email_uuid}_{attachment_name}"
        attachment_path = (Path()/attachment_dir/unique_attachment_name).as_posix() 
        attachment.SaveAsFile(attachment_path)
        attachment_paths.append(attachment_path)
    
    return attachment_paths


def get_email_from_outlook(user_id:str,
                           json_save_loc:Path=None,
                           attachment_dir:Path=None) -> None:
    """ Gets email from Outlook on Windows system saves to json 
    """
    email_data = []
    
    outlook = win32com.client.Dispatch("Outlook.Application").GetNameSpace("MAPI")
    inbox = outlook.Folders(user_id).Folders("Inbox")
    messages = inbox.Items
    for message in messages:
        subject = message.Subject
        # Checks the subject for keyword before processing
        if "Test_App_Email_1234" in subject:
            email_uuid = str(uuid.uuid4())
            body = message.body
            attachments = message.Attachments
            received_time_pywin = message.ReceivedTime
            received_time_dt = datetime.fromtimestamp(received_time_pywin.timestamp()).strftime("%d-%m-%Y- %H:%M:%S")
            attachtment_paths = save_attachments(attachments=attachments, email_uuid=email_uuid)
            email_data.append({
                'uuid':email_uuid,
                'subject':subject,
                'body': body,
                'received_time': received_time_dt,
                'attachments': attachtment_paths 
            })
    
    # If no json_save_loc -> saves to current working dir with filename emails.json
    if json_save_loc is None:
        json_save_loc = Path.cwd()/"emails.json"
    
    with open(file=json_save_loc, mode='w', encoding='utf-8') as json_file:
        json.dump(obj=email_data, fp=json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    EMAIL_ID = os.getenv('EMAIL_ID')
    get_email_from_outlook(user_id=EMAIL_ID)
