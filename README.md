# mail_automation_wf
<img width="424" alt="image" src="https://github.com/almutareb/mail_automation_wf/assets/104657679/9fc2d76a-03fd-42f3-904f-0f6386d37091">

## Overview
This project aims to automate the processing of incoming emails by performing various tasks, including fetching emails, recognizing entities, classifying and summarizing content, enriching data, and drafting responses. This README provides detailed information on the project's goals, agents, tasks, and overall workflow.

### Table of Contents
- Goals
- Agents and Tasks
  - Email Fetcher
  - Attachment Downloader
  - Attachment Processor
  - Entity Recognizer
  - Classifier
  - Data Enricher
  - Data Checker
  - Historical Data Fetcher
  - Email Writer
  - Quality Checker
  - Email Saver
- Workflow
- Installation
- Configuration
- Usage
- Contributing
- License

#### OCR Structuring

in the example code `populated_document_parser.py` and `unpopulated_document_parser.py` we attempt to fill in the blanks from normal OCR using an LLM. Where `populated_document_parser.py` is a filled does OCR on a populated document and `unpopulated_document_parser.py` does OCR on an empty document. **Please Note** Proper formattig into a `Dict` object is not 100% and errors could happen. We are still in the process and refining the output. In addition the example code only is ran on the first page to minize complexity.

##### Repo strcuture
`populated_document_parser.py` and `unpopulated_document_parser.py` belong in the `cookbook` directory, and will be moved there in the future.

##### Additional information
Please check the documentation of tesseract to learn how to
1. download the tesseract executible file
2. download the German language pack, which is needed for the POC

### Code Example

```python
    document_parser = DocumentParser(
        pdf_file_location="examples/blank_documenr.pdf",
        ocr_output_location="test_sample",
    )
    
    
    document_parser.pdf_to_images()
    
    document_text = document_parser.image_to_text()
```
