from langchain_core.prompts import PromptTemplate


user_questions_template = """
Answer the following questions
=================
{JSONOCR} {SUMMARY} 
====================

{QUESTION}

"""

user_questions_prompt = PromptTemplate.from_template(user_questions_template)
