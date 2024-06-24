"""
Code snippet from https://python.langchain.com/v0.2/docs/integrations/llms/huggingface_endpoint/

======
OBSERVATIONS:
Based on my research "mistralai/Mixtral-8x22B-Instruct-v0.1" seems to do a good job.

"""

from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate

from mail_automation_wf.ocr.utils.pdf_to_dir import pdf_to_images
from mail_automation_wf.utils.file_handling import read_file, json_string_to_json

import pytesseract
from pytesseract import Output
from PIL import Image


import re
import json
from typing import Any, Dict

def extract_json_from_string(input_string: str) -> Dict[str, Any]:
    """
    Extracts JSON content from a string that contains JSON data embedded within it.

    Args:
        input_string (str): The input string containing JSON data.

    Returns:
        Dict[str, Any]: The parsed JSON content as a dictionary.
    """
    # Regular expression to match JSON content
    # json_regex = re.compile(r'```json\n({.*?})\n```', re.DOTALL)
    
    pattern = r'```(\w+)\n({.*?})\n```'
    json_regex = re.compile(pattern, re.DOTALL)
    
    # Search for JSON content within the input string
    match = json_regex.search(input_string)
    
    if not match:
        raise ValueError("No JSON content found in the input string.")
    
    # Extract JSON content
    # json_content = match.group(1)
    json_content = match.group(2)
    
    # Parse JSON content
    parsed_json = json.loads(json_content)
    
    return parsed_json

# # Example usage
# input_string = '''```json
# {
#     "company": {
#         "name": "Zander-Versicherung


pdf_path = "examples/populated_document.pdf"


f = pdf_to_images(
    pdf_path=pdf_path,
)

# ocr_data_DICT = pytesseract.image_to_data(Image.open(f[0]),lang="deu",output_type=Output.DICT)
ocr_data_DICT = pytesseract.image_to_data(Image.open(f[1]),lang="deu",output_type=Output.DICT)

all_valid_text = [i for i in ocr_data_DICT['text'] if i.strip()]

template = """ please attempt to organize the {unstrucutred_data} from the OCR 
and try to properly group it and turn it into a json format. Make sure there are no 
comments in the JSON string

"""

prompt = PromptTemplate.from_template(template)


llm = HuggingFaceEndpoint(
  # repo_id="mistralai/Mistral-7B-Instruct-v0.3", 
  repo_id="mistralai/Mistral-7B-Instruct-v0.2", 
  # temperature=1, 
  # max_new_tokens=1024,
  repetition_penalty=1.2,
  return_full_text=False
    )


llm_chain = prompt | llm

json_ouput = llm_chain.invoke({"unstrucutred_data": all_valid_text})

# Will return None if the LLM did not format the output correctly
json_ouput_as_json = json_string_to_json(json_ouput)

parsed_json_ouput_as_json = extract_json_from_string(json_ouput)



# print(str(json_ouput))
print(str(parsed_json_ouput_as_json))
x=0