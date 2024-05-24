import os
from pathlib import Path
from pdf2image import convert_from_path
from typing import List

def pdf_to_images(pdf_path: str, output_dir: str) -> List[str]:
    """
    Convert a PDF to images and save them to the specified directory.

    Args:
        pdf_path (str): The path to the PDF file to convert.
        output_dir (str): The directory where the images will be saved.

    Returns:
        List[str]: A list of file paths to the saved images.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert PDF to images
    images = convert_from_path(pdf_path)
    
    # Save each image and collect their file paths
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(output_dir, f'page_{i + 1}.png')
        image.save(image_path, 'PNG')
        image_paths.append(image_path)
    
    return image_paths

# Example usage
pdf_path = 'example.pdf'  # Path to your PDF file
output_dir = 'output_images'  # Directory where images will be saved

image_paths = pdf_to_images(pdf_path, output_dir)
print(f'Images saved to: {image_paths}')
