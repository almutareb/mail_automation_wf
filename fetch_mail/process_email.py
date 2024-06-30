import pandas as pd
import json
import uuid
from enum import Enum
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import time
import fetch_mail_outlook
from pathlib import Path
import attachment_parser
import fetch_mail.categorize_email as categorize_email


load_dotenv()

HF_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')
EMAIL_ID = os.getenv('EMAIL_ID')


class EmailStatus(Enum):
    PROCESSED = 'processed'
    UNPROCESSED = 'unprocessed'


def check_for_new_mail(emails_jason_file:str, status_file:str):
    """ Checks the json doc for new emails and updates status file """
    with open(file=emails_jason_file, mode='r') as json_file:
        email_data = json.load(json_file)
    
    df = pd.read_csv(filepath_or_buffer=status_file)
    
    for email in email_data:
        if email['entry_id'] not in df['entry_id'].values:
            df.loc[len(df)] = [email['entry_id'], EmailStatus.UNPROCESSED.name, None] 
            df.to_csv(path_or_buf=status_file, index=False)
            print(f"Found new email {email['entry_id'] = }")


def get_unprocessed_emails(status_file:str) -> list[str]:
    """ Returns a list of email entry IDs of un-processed emails """
    df = pd.read_csv(filepath_or_buffer=status_file)
    result = df.loc[df['Status'] == 'UNPROCESSED', 'entry_id'].values
    return result


def get_email_data(email_entry_id:str, emails_jason_file:str) -> dict:
    """ Given an email entry ID returns the email data """
    with open(file=emails_jason_file, mode='r') as json_file:
        email_data = json.load(json_file)
    
    for email in email_data:
        if email['entry_id'] == email_entry_id:
            return email         


def process_emails(unprocessed_emails:list[str], 
                   emails_jason_file:str, 
                   status_file:str, summarize_llm:HuggingFaceEndpoint) -> None:
    """ Summarises the email and parses the attachment """
    for i, entry_id in enumerate(unprocessed_emails):
        email_data = get_email_data(email_entry_id=entry_id, 
                                    emails_jason_file=emails_jason_file)
        # Summarize the email body
        email_body = email_data['body'].replace('\r',' ').replace("\n", " ")

        summary = categorize_email.summarize_email_body(email_body=email_body, 
                                                      llm_model=summarize_llm)
        df = pd.read_csv(filepath_or_buffer=status_file, dtype='object')
        df.loc[df['entry_id'] == entry_id, 'Summary'] = summary
        df.to_csv(path_or_buf=status_file, index=False)

        # # Parse the attachments
        # for attachment_loc in email_data['attachments']:
        #     process_attachment(attachment_loc=attachment_loc)
        
        # df.loc[df['entry_id'] == entry_id, 'Status'] = EmailStatus.PROCESSED
        print(f'Processed {i+1} email') 
    

def update_email_status(entry_id:str, status:EmailStatus, status_file:str) -> None:
    """ Updates the status of an email in csv """
    df = pd.read_csv(filepath_or_buffer=status_file)
    df.loc[df['entry_id'] == entry_id, 'Status'] = status
    df.to_csv(path_or_buf=status_file, index=False)


def process_attachment(attachment_loc:str, save_file_loc:str=None) -> None:
    """ Parses the attachement and saves parsed doc to file """
    if save_file_loc is None:
        save_file_loc = 'processed_attachments'
    attachment_loc_path = Path(attachment_loc)
    if attachment_loc_path.suffix != ".pdf":
        print("Can only handle pdf attachments at the moment")
        return
    attachment_name = attachment_loc_path.parts[-1].split('.')[0]
    result = attachment_parser.parse_attachment(attachment_loc=attachment_loc)
    if result:
        with open(file=f"{attachment_name}_processed.txt", mode='w') as file:
            file.write(result)
    else:
        print('Could not parse attachment')


# def main() -> None:
#     while True:
#         fetch_mail_outlook.get_email_from_outlook(user_id=EMAIL_ID, json_save_loc='emails.json')
#         check_for_new_mail(emails_jason_file='emails.json', status_file='email_status.csv')
#         unprocessed_emails = get_unprocessed_emails(status_file='email_status.csv')
#         process_emails(unprocessed_emails=unprocessed_emails,emails_jason_file='emails.json', status_file='email_status.csv')
#         time.sleep(5 * 60) # Sleep for 5 minutes (5 * 60 seconds)


if __name__ == "__main__":
    
    llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1", 
    temperature=0.1, 
    max_new_tokens=1024,
    repetition_penalty=1.2,
    return_full_text=False,
    huggingfacehub_api_token=HF_API_TOKEN) 

    
    check_for_new_mail(emails_jason_file='emails.json', status_file='email_status.csv')
    unprocessed_emails = get_unprocessed_emails(status_file='email_status.csv')
    process_emails(unprocessed_emails=unprocessed_emails,
                   emails_jason_file='emails.json', 
                   status_file='email_status.csv',
                   summarize_llm=llm)
