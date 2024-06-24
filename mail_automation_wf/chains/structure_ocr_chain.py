from langchain_core.prompts import PromptTemplate


ocr_structure_template = """ convert
=================
{unstrucutred_data} 
====================
try to organize and convert into json

"""

ocr_structure_prompt = PromptTemplate.from_template(ocr_structure_template)


# llm_chain = prompt | llm