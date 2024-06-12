import os
from pathlib import Path
from pdf2image import convert_from_path
from typing import List, NoReturn, Dict
import pytesseract
from pytesseract import Output
from PIL import Image

class DocumentParser:
    """
    DocumentParser is an object with the goal of handling the results from OCR
    
    ## Keyword arguments:
    - pdf_file_location  (str) 
    - ocr_output_location (str)
    
    Return: return_description
    """
    
    
    def __init__(
        self, 
        pdf_file_location:str,
        ocr_output_location = "ocr_output",
        ):
        self.pdf_file_location = pdf_file_location
        self.ocr_output_location = ocr_output_location
        self.pdf_images = []
        
        
    def pdf_to_images(
        self,
        # pdf_path: str, 
        # output_dir: str="output_dir"
        ) -> NoReturn:
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
    
    dd = DocumentParser(
        pdf_file_location="examples/blank_documenr.pdf",
        ocr_output_location="test_sample",
    )
    dd.pdf_to_images()
    data = dd.image_to_text()
    x = 0