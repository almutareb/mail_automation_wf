from mail_automation_wf.document_parser.document_parser import DocumentParser
from mail_automation_wf.utils.file_handling import  (
    extract_json_from_string, json_string_to_json
)
from typing import List, Dict, Any
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate



if __name__ == "__main__":
    document_parser = DocumentParser(
        pdf_file_location="examples/blank_documenr.pdf",
        ocr_output_location="test_sample",
    )
    
    document_parser.pdf_to_images()
    
    data = document_parser.image_to_text()
    
    all_valid_text = [i['text'] for i in data]
    
    new_all_valid_text = []
    
    for text in all_valid_text:
        filter_text =  [i for i in text if i.strip()]
        new_all_valid_text.append([filter_text])
        
    
    template = """ convert
    =================
    {unstrucutred_data} 
    ====================
    from the OCR into json that is compatible with json

    """
    # template = """ organize {unstrucutred_data} from the OCR 
    # and try to properly group it and turn it into a json .  
    # """

    prompt = PromptTemplate.from_template(template)

    llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3", 
    # repo_id="mistralai/Mistral-7B-Instruct-v0.2", 
    # temperature=1, 
    max_new_tokens=1024,
    repetition_penalty=1.2,
    return_full_text=False
        )
    
    llm_chain = prompt | llm

    sample_text = new_all_valid_text[0]
    temp_data_name:List[str] = [llm_chain.invoke({"unstrucutred_data": i}) for i in sample_text]
    
    try: 
        sample = extract_json_from_string(temp_data_name[0])
    except:
        print("something whent wrong")
        
    try:
        sample = json_string_to_json(temp_data_name[0])
    except:
        print("something whent wrong")
    
    x = 0