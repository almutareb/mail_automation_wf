from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
import pytesseract
from pytesseract import Output
from PIL import Image
from pathlib import Path
import sys

current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent    
sys.path.append(str(parent_dir))

from mail_automation_wf.ocr.utils.pdf_to_dir import pdf_to_images
from mail_automation_wf.utils.file_handling import read_file, json_string_to_json


def parse_attachment(attachment_loc:str) -> str:
    try:
        f = pdf_to_images(pdf_path=attachment_loc)
    except Exception as e:
        print(f"Could not open pdf file:\n{attachment_loc=}\n", e)
        return
    ocr_data_DICT = pytesseract.image_to_data(Image.open(f[0]), lang="deu", output_type=Output.DICT)
    
    all_valid_text = [i for i in ocr_data_DICT['text'] if i.strip()]

    
    template = """ please attempt to organize the {unstrucutred_data} from the OCR 
    and try to properly group it and turn it into a json format.  
    """
    prompt = PromptTemplate.from_template(template)

    llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3", 
    temperature=0.1, 
    max_new_tokens=1024,
    repetition_penalty=1.2,
    return_full_text=False)


    llm_chain = prompt | llm

    json_ouput = llm_chain.invoke({"unstrucutred_data": all_valid_text})
    
    # Will return None if the LLM did not format the output correctly
    json_ouput_as_json = json_string_to_json(json_ouput)

    return json_ouput

if __name__ == "__main__":
    parsed = parse_attachment(attachment_loc='Attachments/7e8bda29-923d-44f5-9878-3340be26683a_schadenanzeige_haftpflicht-2.pdf')
    print(f'{parsed =}')
    
    # print(f'{parent_dir =}')