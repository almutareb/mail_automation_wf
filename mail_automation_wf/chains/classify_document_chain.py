from langchain_core.prompts import PromptTemplate

classify_chain_template = """ 
    =================
    {document} 
    ====================
    classify the type of docuemnt this is
    """
    
document_classification_chain_prompt = PromptTemplate.from_template(classify_chain_template)
