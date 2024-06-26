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

def get_relative_path(project_dir:str):
    """ Takes the name of project directory and returns the relative path 
        to the current working directory """
    
    # Get the current working directory
    current_working_directory = Path.cwd()

    # Define the base directory name you want to be relative to
    base_directory_name = project_dir

    # Traverse upwards to find the base directory
    for parent in current_working_directory.parents:
        if parent.name == base_directory_name:
            base_directory = parent
            break
    else:
        base_directory = None

    if base_directory:
        # Get the relative path from the base directory
        relative_path = current_working_directory.relative_to(base_directory)
        result = Path(base_directory_name) / relative_path
        return result
    else:
        print(f"The base directory '{base_directory_name}' was not found in the path.")


def save_attachments(attachments:list,
                     email_entry_id:str,
                     attachment_dir:str=None) -> list[str]:
    """ Saves the attachments to a folder """
    
    attachment_paths = []
    
    # If attachment_dir == None, then creates an Attachments folder in cwd 
    if attachment_dir is None:
        # Make an attachment dir
        attachment_dir = Path.cwd()/"Attachments"
        if not attachment_dir.exists():
            attachment_dir.mkdir(parents=True, exist_ok=True)
        # Get relative path to attachments 
        project_dir = Path.cwd().parent.parent.name
        project_dir_idx = Path.cwd().parts.index(project_dir)
        relative_path = '/'.join(Path.cwd().parts[project_dir_idx:])
        relative_path_attachments = Path()/relative_path/"Attachments"
    else:
        project_dir = Path.cwd().parent.parent.name
        relative_path_attachments = get_relative_path(project_dir=project_dir)

    for attachment in attachments:
        attachment_name = attachment.FileName
        unique_attachment_name = f"{email_entry_id}_{attachment_name}"
        relative_attachment_path = relative_path_attachments / unique_attachment_name
        actual_attachment_path = attachment_dir/unique_attachment_name
        if actual_attachment_path.is_file():
            print(f"{actual_attachment_path} already exists - not saving to file")
        else:
            attachment.SaveAsFile(str(actual_attachment_path))

        attachment_paths.append("/".join(relative_attachment_path.parts))
    
    return attachment_paths


def get_email_from_outlook(user_id:str,
                           json_save_loc:Path=None,
                           attachment_dir:Path=None) -> None:
    """ Gets email from Outlook on Windows system saves to json """
    email_data = []
    
    outlook = win32com.client.Dispatch("Outlook.Application").GetNameSpace("MAPI")
    inbox = outlook.Folders(user_id).Folders("Inbox")
    messages = inbox.Items
    for message in messages:
        subject = message.Subject
        # Checks the subject for keyword before processing
        if "Test_App_Email_1234" in subject:
            print(message.Subject)
            print(message.EntryID)
            email_entry_id = message.EntryID
            body = message.body
            attachments = message.Attachments
            received_time_pywin = message.ReceivedTime
            received_time_dt = datetime.fromtimestamp(received_time_pywin.timestamp()).strftime("%d-%m-%Y- %H:%M:%S")
            attachtment_paths = save_attachments(attachments=attachments, email_entry_id=email_entry_id, attachment_dir=attachment_dir)
            from_email = message.SenderEmailAddress
            
            print(f'Found message in inbox {subject=}, {received_time_dt = }')

            email_data.append({
                'entry_id':email_entry_id,
                'from':from_email,
                'to': user_id,
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
    
    