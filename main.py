from pathlib import Path
import json
from fetch_mail.gmail_api import get_service, get_emails
from fetch_mail.categorize_email import add_email_category_to_json
from ocr_processing.document_parser.document_parser import DocumentParser


def main() -> None:

    # Authenticate Gmail 
    service = get_service(credentials_json='fetch_mail/credentials.json', token_file='fetch_mail/token.pickle')

    # Get emails
    message_ids = get_emails(service=service,
                             subject_filter = "Test_App_Email_1234",
                             attachment_dir = 'working/attachments',
                             emails_json_dir = 'working/emails_json',
                             status_file = 'working/email_status.csv')
    
    # Go through all the emails and add categories -> does not check if already categorized
    for email_file in Path('working/emails_json').iterdir():
        add_email_category_to_json(email_json_file=email_file, status_file='working/email_status.csv')
        print('Categorizing email')


if __name__ == "__main__":

    main()

    # Loop through all the emails json                
    for email_file in Path('working/emails_json').iterdir():
        with open(file=email_file, mode='r') as json_file:
            email_data = json.load(json_file)
        
        # Get the message id of the email
        message_id = email_data['id']
        
        # Loop through the attachments
        for attachment in email_data['attachments']:
            # Check for specific attachment
            if attachment == "schadenanzeige_haftpflicht-2.pdf":
                attachment_path = Path().cwd()/"working"/"attachments"/str(message_id)/attachment
                assert attachment_path.is_file(), "Cannot find file"
                print(f'{attachment_path=}')

                # attachment_ocr = DocumentParser(pdf_file_location=attachment_path)


    