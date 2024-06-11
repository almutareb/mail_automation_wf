import os
from pathlib import Path
from pdf2image import convert_from_path
from typing import List, NoReturn

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
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Convert PDF to images
        images = convert_from_path(self.pdf_file_location)
        
        # Save each image and collect their file paths


        for i, image in enumerate(images):
            image_path = os.path.join(self.output_dir, f'page_{i + 1}.png')
            image.save(image_path, 'PNG')
            self.pdf_images.append(image_path)
            
    
        