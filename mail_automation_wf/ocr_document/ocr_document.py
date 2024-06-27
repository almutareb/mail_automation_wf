from typing import Dict

class OCRDocument:
    
    def __init__(
        self, 
        page_num, 
        image_location,
        document_lang,
        ocr_metadata:Dict,
        *args, 
        **kwargs
        ):
        
        self.page_num = page_num
        self.image_location = image_location
        self.document_lang = document_lang
        self.ocr_metadata = ocr_metadata
        self.text =  [i for i in [ocr_metadata['text']][0] if i.strip()]
        
        
    