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

load_dotenv()

HF_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')
EMAIL_ID = os.getenv('EMAIL_ID')


class EmailStatus(Enum):
    PROCESSED = 'processed'
    UNPROCESSED = 'unprocessed'


def check_for_new_mail(emails_jason_file:str, status_file:str):
    """ Checks the json doc for new emails """
    with open(file=emails_jason_file, mode='r') as json_file:
        email_data = json.load(json_file)
    
    df = pd.read_csv(filepath_or_buffer=status_file)
    
    for email in email_data:
        if email['uuid'] not in df['email_UUID'].values:
            df.loc[len(df)] = [email['uuid'], EmailStatus.UNPROCESSED.name, None] 
            df.to_csv(path_or_buf=status_file, index=False)
            print(f"Found new email {email['uuid'] = }")


def get_unprocessed_emails(status_file:str) -> list[uuid.uuid4]:
    """ Returns a list of UUID values of un-processed emails """
    df = pd.read_csv(filepath_or_buffer=status_file)
    result = df.loc[df['Status'] == 'UNPROCESSED', 'email_UUID'].values
    return result


def get_email_data(email_uuid:uuid.uuid4, emails_jason_file:str) -> dict:
    """ Given an email uuid returns the email data """
    with open(file=emails_jason_file, mode='r') as json_file:
        email_data = json.load(json_file)
    
    for email in email_data:
        if email['uuid'] == email_uuid:
            return email         


def process_emails(unprocessed_emails:list[uuid.uuid4], emails_jason_file:str, status_file:str) -> None:
    """ Summarises the email and parses the attachment """
    df = pd.read_csv(filepath_or_buffer=status_file) 
    for i, email_uuid in enumerate(unprocessed_emails):
        email_data = get_email_data(email_uuid=email_uuid, emails_jason_file=emails_jason_file)
        email_body = email_data['body'].replace('\r','').replace("\n", "")
        summary = summarize_email_body(email_body=email_body)
        df.loc[df['email_UUID'] == email_uuid, 'Summary'] = summary
        
        for attachment_loc in email_data['attachments']:
            parse_attachment(attachment_loc=attachment_loc)
            # Write status to CSV -> store the json on disk
        
        print(f'Processed {i+1} email') 
    df.to_csv(path_or_buf=status_file, index=False)


def update_email_status(email_uuid:uuid, status:EmailStatus, status_file:str) -> None:
    """ Updates the status of an email in csv """
    df = pd.read_csv(filepath_or_buffer=status_file)
    df.loc[df['email_UUID'] == email_uuid, 'Status'] = status
    df.to_csv(path_or_buf=status_file, index=False)


def summarize_email_body(email_body:str) -> str:
    """ Summarizes email body """
    llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1", 
    temperature=0.1, 
    max_new_tokens=1024,
    repetition_penalty=1.2,
    return_full_text=False,
    huggingfacehub_api_token=HF_API_TOKEN) 

    template = """Summarize this email in a few words:\n{email_body} """
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    summary = chain.invoke({'email_body':email_body})
    return summary


def parse_attachment(attachment_loc:str) -> json:
    """ Use populated_document_parser """
    loc = "D:\\singh\\Documents\\Mail_Automation_WF\\mail_automation_wf\\Fetch Mail\\Attachments\\7e8bda29-923d-44f5-9878-3340be26683a_schadenanzeige_haftpflicht-2.pdf"

def main() -> None:
    while True:
        fetch_mail_outlook.get_email_from_outlook(user_id=EMAIL_ID, json_save_loc='emails.json')
        check_for_new_mail(emails_jason_file='emails.json', status_file='email_status.csv')
        unprocessed_emails = get_unprocessed_emails(status_file='email_status.csv')
        process_emails(unprocessed_emails=unprocessed_emails,emails_jason_file='emails.json', status_file='email_status.csv')
        time.sleep(5 * 60) # Sleep for 5 minutes (5 * 60 seconds)


if __name__ == "__main__":
    bod = "Dear Sir,\r\n\r\n \r\n\r\nThis is to inform you that I while I was practicing golf in my backyard, an errant shot broke my neighbour’s window. He has asked me to replace his window and I would like to claim this expense against my home insurance policy. \r\n\r\nPlease find attached my policy claim form duly filled. \r\n\r\n \r\n\r\nBest regards,\r\n\r\n \r\n\r\nAstrix Gallier\r\nTel: +43 (151) 017565893214  \r\n"
    bod = bod.replace('\r','').replace("\n", "")
    summary = summarize_email_body(email_body=bod)
    print(f'{summary=}')
    # unprocessed_emails = get_unprocessed_emails(status_file='email_status.csv')
    # process_emails(unprocessed_emails=unprocessed_emails,emails_jason_file='emails.json', status_file='email_status.csv')