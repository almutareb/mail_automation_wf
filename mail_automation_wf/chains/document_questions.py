from langchain_core.prompts import PromptTemplate


document_qa_template = """
Answer the following questions
=================
{JSONOCR} {SUMMARY} 
====================

1. Is is the insured
2. Insurer address
3. Policy Number
4. Where is this event took place
5. when did this event took place


"""

document_qa_prompt = PromptTemplate.from_template(document_qa_template)
