from nougat.utils.checkpoint import get_checkpoint
import subprocess
import uuid
import requests
import time
import re


CHECKPOINT = get_checkpoint('nougat')

# Download pdf from a given link
def get_pdf(pdf_link):
  # Generate a unique filename
  unique_filename = f"content/input/download_paper_{uuid.uuid4().hex}.pdf"

  # send a GET request to the PDF link
  response = requests.get(pdf_link)

  if response.status_code == 200:
    # save the PDF content to a local file
    with open(unique_filename, 'wb') as pdf_file:
      pdf_file.write(response.content)
    print("PDF downloaded successfully.")
  else:
    print("Failed to download the PDF.")
  return unique_filename

# Run nougat on the pdf file
def nougat_ocr(file_name):

  # cli command to run
  cli_command = [
      'nougat',
      '--out', 'content/output/',
      'pdf', file_name,
      '--checkpoint', CHECKPOINT,
      '--markdown',
      '--no-skipping'
  ]

  print(f'run this: {cli_command}')

  # Run the command
  subprocess.run(cli_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

  return

# predict function / driver function
def paper_read(pdf_file=None, pdf_link=None):
  if pdf_file is None:
    if pdf_link == '':
      print("No file is uploaded and no link is provided")
      return "No data provided. Upload a pdf file or provide a pdf link and try again!"
    else:
      file_name = get_pdf(pdf_link)
  else:
    file_name = pdf_file
    print(f'file name is {file_name}')

  nougat_ocr(file_name)

  #Open the file for reading
  file_name = file_name.split('/')[-1][:-4]
  with open(f'content/output/{file_name}.mmd', 'r') as file:
   content = file.read()

  return content

st = time.time() # Start time for performance measurement
content = paper_read(None, 'https://arxiv.org/pdf/2309.03883v1.pdf')

et = time.time() - st # Calculate time taken for splitting
print(f'created markdown file in {et} seconds.')

print(content)