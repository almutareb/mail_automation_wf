from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import HumanMessagePromptTemplate, AIMessagePromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
import os

load_dotenv()


def summarize_email_body(email_body:str, 
                         llm_model:HuggingFaceEndpoint) -> str:
    """ Summarizes email body """
    
    system_template = ("Summarize the contents of an email." 
                      " Be concise and do not use more than 20 words."
                       " Respond only with the summary text.")
    system_message_prompt = SystemMessagePromptTemplate.from_template(template=system_template)

    human_template1 = ("email: I am writing to inquire about the details of my current insurance policy, "
                        "specifically regarding coverage limits and any upcoming renewal procedures. " 
                        "Could you please provide me with the relevant information at your earliest convenience?")
    human_message_prompt1 = HumanMessagePromptTemplate.from_template(template=human_template1)

    example_message1 = """summary: Requesting details about current insurance policy coverage and renewal procedures."""
    example_output1 = AIMessagePromptTemplate.from_template(template=example_message1)

    human_template2 = ("email: I am writing to report a car accident that occurred on 12.Jun.2022 at Waterloo. "
                       "My policy number is 1234567. Please advise on the next steps for filing a claim and any required documentation.")
    human_message_prompt2 = HumanMessagePromptTemplate.from_template(template=human_template2)

    example_message2 = """summary: Vehicle insurance claim from accident. Policy number provided."""
    example_output2 = AIMessagePromptTemplate.from_template(template=example_message2)

    data_template = """email: {email}"""
    data_prompt = HumanMessagePromptTemplate.from_template(data_template)

    chat_prompt = ChatPromptTemplate.from_messages(messages=[system_message_prompt, 
                                                         human_message_prompt1, 
                                                         example_output1, 
                                                         human_message_prompt2, 
                                                         example_output2, data_prompt])
    
    chain = chat_prompt | llm_model | StrOutputParser()

    result = chain.invoke({'email':email_body})
    
    # Find 'summary:' in the result and take text from that
    key_words = ['summary:', 'Summary:']
    for keyword in key_words:
        if keyword in result:
            id = result.find(keyword)
            summary = result[id+(len(keyword)):].strip()
            break
        else:
            print(f"Could not find keyword in result -> returning result as is")
            summary = result

    return summary


if __name__ == "__main__":
    
    HF_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN')
    
    llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1", 
    temperature=0.1, 
    max_new_tokens=1024,
    repetition_penalty=1.2,
    return_full_text=False,
    huggingfacehub_api_token=HF_API_TOKEN) 

    email_body2 = "Dear Insurance Company,\r\n\r\n\r\n\r\nHere's the short version: I reached for a jar of spaghetti sauce on the top shelf, but it had other ideas. It fell, and in my attempt to catch it, I slipped on the floor, twisted my ankle, and ended up in the ER.\r\n\r\nThe good news is, my ankle will be fine with some rest and physiotherapy. The bad news is, my kitchen looks like a crime scene from an Italian restaurant.\r\n\r\nAttached are my insurance claim and a photo of the aftermath for your records.\r\n\r\nThanks for your help!\r\n\r\n \r\n\r\nBest,\r\n\r\n \r\n\r\nK. Singh\r\n\r\nPolicy Number: ABC987654\r\n\r\n \r\n"

    summary = summarize_email_body(email_body=email_body2, llm_model=llm)
    print(summary)
