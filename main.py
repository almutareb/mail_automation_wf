from mail_automation_wf.document_parser.document_parser import DocumentParser
from mail_automation_wf.utils.file_handling import  (
    extract_json_from_string, json_string_to_json
)
from typing import List, Dict, Any
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from mail_automation_wf.chains import (
    ocr_structure_prompt,
    json_summary_chain_prompt,
    document_classification_chain_prompt,
    document_qa_prompt,
    )

if __name__ == "__main__":
    document_parser = DocumentParser(
        pdf_file_location="examples/blank_documenr.pdf",
        # pdf_file_location="examples/populated_document.pdf",
        ocr_output_location="test_sample",
    )
    
    document_parser.pdf_to_images()
    
    data = document_parser.image_to_text()
    
    ocr_document_text:List[str] = [i.text for i in document_parser.ocr_documents]
    

    llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3", 
    # repo_id="mistralai/Mistral-7B-Instruct-v0.2", 
    # repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1", 
    # repo_id="microsoft/Phi-3-medium-128k-instruct", 
    # repo_id="meta-llama/Meta-Llama-3-8B-Instruct", 
    # temperature=1, 
    max_new_tokens=1024,
    # max_new_tokens=2024,
    repetition_penalty=1.2,
    return_full_text=False
        )
    
    

    sample_text = ocr_document_text [0]
    
    mid_index = len(sample_text) // 2

    sample_text = sample_text[:mid_index], sample_text[mid_index:]



    ocr_structure_chain = ocr_structure_prompt | llm
    temp_data_name:List[str] = [ocr_structure_chain.invoke({"unstrucutred_data": i}) for i in sample_text]
    
    try: 
        ocr_json = extract_json_from_string(temp_data_name[0])
        print("pre-processing document was successful")
    except:
        print("Issue pre parsing the json")
        
    try:
        ocr_json = json_string_to_json(temp_data_name[0])
        print("Sucessful without preproccessing")
    except:
        print("parsing unsuccessfull")
        
        
    # allow the user the create categories
    # make a summary
    # create a ticket
    
    
    summary_chain = json_summary_chain_prompt | llm
    
    data_sample = summary_chain.invoke({"unstrucutred_data": str(ocr_json)})
    
    
    
    classify_document_chain = document_classification_chain_prompt | llm 
    
    classify_sample = classify_document_chain.invoke({"document": str(ocr_json)})
    
    #5 Questions
    # who is the insured
    # Insurer address
    # policy number
    # summary of case
    # where
    # when
    
    document_qa_chain = document_qa_prompt | llm
    
    qa_answers = document_qa_chain.invoke({"JSONOCR": str(ocr_json), "SUMMARY": data_sample})
    
    x = 0