
"""

This is where our chains are stored
"""

from mail_automation_wf.chains.structure_ocr_chain import ocr_structure_prompt
from mail_automation_wf.chains.json_summary_chain import json_summary_chain_prompt
from mail_automation_wf.chains.classify_document_chain import document_classification_chain_prompt
from mail_automation_wf.chains.document_questions import document_qa_prompt
from mail_automation_wf.chains.user_question_chain import user_questions_prompt
