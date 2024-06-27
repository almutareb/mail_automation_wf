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
    user_questions_prompt
    )

if __name__ == "__main__":
    document_parser = DocumentParser(
        # pdf_file_location="examples/blank_documenr.pdf",
        pdf_file_location="examples/populated_document.pdf",
        ocr_output_location="test_sample",
    )
    
    document_parser.pdf_to_images()
    
    data = document_parser.image_to_text()
    
    ocr_document_text:List[str] = [i.text for i in document_parser.ocr_documents]
    

    llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.3", 
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
        
    
    summary_chain = json_summary_chain_prompt | llm
    
    document_summary = summary_chain.invoke({"unstrucutred_data": str(ocr_json)})
    
    
    classify_document_chain = document_classification_chain_prompt | llm 
    
    document_type = classify_document_chain.invoke({"document": str(ocr_json)})
    
    document_qa_chain = document_qa_prompt | llm
    
    qa_answers = document_qa_chain.invoke({"JSONOCR": str(ocr_json), "SUMMARY": document_summary})
    
    
    user_questions = [
        "who is the insured?",
        "What is the Insurer address?",
        "What is the Policy Number?",
        "Where did this event take place?",
        "when did this event take place?",
        "What happened based on this document",
    ]
    
    user_question_chain = user_questions_prompt | llm
    
    answered_user_questions = []
    for questions in user_questions:
        temp_answer = user_question_chain.invoke({"JSONOCR": str(ocr_json), "SUMMARY": document_summary, "QUESTION":questions})
        answered_user_questions.append(temp_answer)
        
    x = 0