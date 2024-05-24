# https://tesseract-ocr.github.io/tessdoc/Installation.html
# https://pypi.org/project/pytesseract/

from PIL import Image
import pytesseract

if __name__ == "__main__":
    file_location = "assets/flow-chart.png"

    print(pytesseract.image_to_data(Image.open(file_location)))