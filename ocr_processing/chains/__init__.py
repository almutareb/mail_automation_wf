
"""

This is where our chains are stored
"""

from ocr_processing.chains.structure_ocr_chain import ocr_structure_prompt
from ocr_processing.chains.json_summary_chain import json_summary_chain_prompt
from ocr_processing.chains.classify_document_chain import document_classification_chain_prompt
from ocr_processing.chains.document_questions import document_qa_prompt
from ocr_processing.chains.user_question_chain import user_questions_prompt

