from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

HF_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')
    

LLM = HuggingFaceEndpoint(
repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1", 
temperature=0.1, 
max_new_tokens=1024,
repetition_penalty=1.2,
return_full_text=False,
huggingfacehub_api_token=HF_API_TOKEN) 


def categorize_email(email_body:str,
                     llm_model:HuggingFaceEndpoint = LLM) -> str:
    """ Summarizes email body """
    
    template = (
        """
        You are a customer service bot. Your task is to assess customer intent 
        and categorize customer inquiry after <<<>>> into one of the following predefined categories:
        
        health insurance claim
        vehicle insurance claim
        home insurance claim
        third party liability insurance
        update customer information
        request for information
        charge dispute
        
        If the text doesn't fit into any of the above categories, classify it as:
        customer service
        
        You will only respond with the predefined category. Do not include the word "Category". Do not provide explanations or notes.
        Do not include the original message in the response.  
        
        ####
        Here are some examples:
        
        Inquiry: I am writing to inquire about the details of my current insurance policy, specifically regarding coverage limits and any upcoming renewal procedures. Could you please provide me with the relevant information at your earliest convenience?
        Category: request for information
        Inquiry: I am writing to report a car accident that occurred on 12.Jun.2022 at Waterloo. My policy number is 1234567. Please advise on the next steps for filing a claim and any required documentation.
        Category: vehicle insurance claim
        ###
    
        <<<
        Inquiry: {email}
        >>>
        """
    )

    prompt = PromptTemplate.from_template(template=template)
    
    chain = prompt | llm_model | StrOutputParser()
    result = chain.invoke({'email': email_body})
    return result.strip()


def add_email_category_to_json(email_json_file:str, status_file:str) -> None:
    """
    Adds category to json and updates status

    """
    with open(file=email_json_file, mode='r') as json_file:
        email_data = json.load(json_file)

    email_body = email_data['body']
    email_data['category'] = categorize_email(email_body=email_body)
    
    with open(file=email_json_file, mode='w', encoding='utf-8') as file:
        json.dump(obj=email_data, fp=file, indent=4)

    # Update the status file
    message_id = email_data['id']
    df = pd.read_csv(filepath_or_buffer=status_file)
    df.loc[df['message_id'] == message_id, 'email_categorized'] = True
    df.to_csv(path_or_buf=status_file, index=False)
            

        



if __name__ == "__main__":
    
    email_body2 = "Dear Sir,\r\n\r\n \r\n\r\nThis is to inform you that I while I was practicing golf in my backyard, an errant shot broke my neighbour's window. He has asked me to replace his window and I would like to claim this expense against my home insurance policy. \r\n\r\nPlease find attached my policy claim form duly filled. \r\n\r\n \r\n\r\nBest regards,\r\n\r\n \r\n\r\nAstrix Gallier\r\nTel: +43 (151) 017565893214  \r\n,"
    email_body1 = "Dear Insurance Company,\r\n\r\n\r\n\r\nHere's the short version: I reached for a jar of spaghetti sauce on the top shelf, but it had other ideas. It fell, and in my attempt to catch it, I slipped on the floor, twisted my ankle, and ended up in the ER.\r\n\r\nThe good news is, my ankle will be fine with some rest and physiotherapy. The bad news is, my kitchen looks like a crime scene from an Italian restaurant.\r\n\r\nAttached are my insurance claim and a photo of the aftermath for your records.\r\n\r\nThanks for your help!\r\n\r\n \r\n\r\nBest,\r\n\r\n \r\n\r\nK. Singh\r\n\r\nPolicy Number: ABC987654\r\n\r\n \r\n"
    email_body3 = "I was driving drunk when I got into an accident, now I want money."

    result = categorize_email(email_body=email_body3, llm_model=LLM)
    print(f"{result = }")


    