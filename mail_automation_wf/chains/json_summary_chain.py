from langchain_core.prompts import PromptTemplate

json_summary_chain_template = """ 
=================
{unstrucutred_data} 
====================
based on this json file summurize what this json is 

"""

json_summary_chain_prompt = PromptTemplate.from_template(json_summary_chain_template)
