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

        Args:
            pdf_path (str): The path to the PDF file to convert.
            output_dir (str): The directory where the images will be saved.

        Returns:
            List[str]: A list of file paths to the saved images.
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
        
        Keyword arguments:
        argument -- description
        Return: return_description
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
        new_all_valid_text.extend(filter_text)
    
    template = """ please attempt to organize the {unstrucutred_data} from the OCR 
    and try to properly group it and turn it into a json format.  
    """

    prompt = PromptTemplate.from_template(template)


    llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3", 
    temperature=0.1, 
    max_new_tokens=1024,
    repetition_penalty=1.2,
    return_full_text=False
        )


    llm_chain = prompt | llm

    
    temp_data_name:List[str] = [llm_chain.invoke({"unstrucutred_data": i}) for i in new_all_valid_text]

    # Will return None if the LLM did not format the output correctly
    json_ouput_as_json:List[Dict] = [json_string_to_json(i) for i in temp_data_name]

    x = 0