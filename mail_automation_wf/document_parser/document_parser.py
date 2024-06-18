import os
from pathlib import Path
from pdf2image import convert_from_path
from typing import List, Dict, Any
import pytesseract
from pytesseract import Output
from PIL import Image

from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
import json
import re
# from mail_automation_wf.utils.file_handling import  json_string_to_json

def json_string_to_json(json_string: str) -> Any:
    """
    Converts a JSON string into a JSON object.

    Args:
        json_string (str): The JSON string to be converted.

    Returns:
        Any: The resulting JSON object (usually a dict or list).
    """
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"An error occurred while parsing the JSON string: {e}")
        return None
    
def extract_json_from_string(input_string: str) -> Dict[str, Any]:
    """
    Extracts JSON content from a string that contains JSON data embedded within it.

    Args:
        input_string (str): The input string containing JSON data.

    Returns:
        Dict[str, Any]: The parsed JSON content as a dictionary.
    """
    # Regular expression to match JSON content
    json_regex = re.compile(r'```json\n({.*?})\n```', re.DOTALL)
    
    # Search for JSON content within the input string
    match = json_regex.search(input_string)
    
    if not match:
        raise ValueError("No JSON content found in the input string.")
    
    # Extract JSON content
    json_content = match.group(1)
    
    # Parse JSON content
    parsed_json = json.loads(json_content)
    
    return parsed_json



class DocumentParser:
    """
    DocumentParser is an object with the goal of handling the results from OCR
    
    ## Keyword arguments:
    - pdf_file_location  (str) 
    - ocr_output_location (str)
    
    
    """
    
    
    def __init__(
        self, 
        pdf_file_location:str,
        ocr_output_location = "ocr_output",
        ):
        self.pdf_file_location = pdf_file_location
        self.ocr_output_location = ocr_output_location
        self.pdf_images: List[str] = []
        
        
    def pdf_to_images(
        self,
        ) -> None:
        """
        Convert a PDF to images and save them to the specified directory.

        ## Args:

        ## Returns:
            None
        """
        # Ensure output directory exists
        os.makedirs(self.ocr_output_location, exist_ok=True)
        
        # Convert PDF to images
        images = convert_from_path(self.pdf_file_location)
        
        # Save each image and collect their file paths


        for i, image in enumerate(images):
            image_path = os.path.join(self.ocr_output_location, f'page_{i + 1}.png')
            image.save(image_path, 'PNG')
            self.pdf_images.append(image_path)
            
    def image_to_text(
        self,
        ocr_output_type=Output.DICT,
        lang="deu",
        **kwargs
        ) -> List[Dict]:
        """This function runs ocr on the given images
        After running OCR on the pdf images, 
        ## Keyword arguments:
        ## argument
        - ocr_output_type : the type of outputs you want the ocr to return
        - lang: the language of the document images. Default to "deu" or german
        ## Return: 
        - None
        """
        
        data = []
        for i in self.pdf_images:
            temp_output = pytesseract.image_to_data(
                Image.open(
                    i),
                    lang=lang,
                    output_type=ocr_output_type,
                )
            data.append(temp_output)
        return data
    
if __name__ == "__main__":
    
    document_parser = DocumentParser(
        pdf_file_location="examples/blank_documenr.pdf",
        ocr_output_location="test_sample",
    )
    
    
    document_parser.pdf_to_images()
    
    data = document_parser.image_to_text()
    
    # get the text from all pages
    all_valid_text = [i['text'] for i in data]
    
    new_all_valid_text = []
    
    for text in all_valid_text:
        filter_text =  [i for i in text if i.strip()]
        new_all_valid_text.append([filter_text])
        
    
    template = """ please attempt to organize the {unstrucutred_data} from the OCR 
    and try to properly group it and turn it into a json format.  
    """

    prompt = PromptTemplate.from_template(template)


    # llm = HuggingFaceEndpoint(
    # repo_id="mistralai/Mistral-7B-Instruct-v0.3", 
    # temperature=0.1, 
    # # max_new_tokens=1024,
    # repetition_penalty=1.2,
    # return_full_text=False
    #     )

    llm = HuggingFaceEndpoint(
    # repo_id="mistralai/Mistral-7B-Instruct-v0.3", 
    repo_id="mistralai/Mistral-7B-Instruct-v0.2", 
    # temperature=1, 
    # max_new_tokens=1024,
    repetition_penalty=1.2,
    return_full_text=False
        )


    llm_chain = prompt | llm

    sample_text = new_all_valid_text[0]
    temp_data_name:List[str] = [llm_chain.invoke({"unstrucutred_data": i}) for i in sample_text]

    # Will return None if the LLM did not format the output correctly
    # json_ouput_as_json:List[Dict] = [extract_json_from_string(i) for i in temp_data_name]
    sample = []
    for i in temp_data_name:
        try:
            data = extract_json_from_string(i)
            sample.append(data)
        except:
            print("hmm")
        try:
            alt_data = json_string_to_json(i)
            sample.append(alt_data)
        except:
            print("thing")
    
    print(data)

    x = 0