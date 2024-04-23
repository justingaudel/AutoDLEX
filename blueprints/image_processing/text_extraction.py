from flask import Blueprint, request
from db_utils import get_db_connection
import cv2
import numpy as np
import pytesseract 
import os
from werkzeug.utils import secure_filename

db_connection = get_db_connection()
cursor = db_connection.cursor()

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

text_extraction_bp = Blueprint("text_extraction",__name__,template_folder="templates")

@text_extraction_bp.route('/process_image', methods=['POST'])
def process_image():
    try:
        if 'image' not in request.files:
            return "No image provided"

        # Read the image file sent from the frontend
        image_data = request.files['image'].read()
        
        
  
        # Convert the image bytes to a numpy array
        nparr = np.frombuffer(image_data, np.uint8)

        # Decode numpy array into an image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Dilation on the green channel
        dilated_img = cv2.dilate(image[:, :, 1], np.ones((7, 7), np.uint8))

        # Median blur to get the background image
        bg_img = cv2.medianBlur(dilated_img, 21)

        # Absolute difference to preserve edges
        diff_img = 255 - cv2.absdiff(image[:, :, 1], bg_img)

        # Normalizing between 0 to 255
        norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)

        # Thresholding
        th = cv2.threshold(norm_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # Perform OCR on the thresholded image
        extracted_text = pytesseract.image_to_string(th)
        extracted_text = extracted_text.split('\n')
        return extracted_text
    
        
    except Exception as e:
        return f"Error processing image: {str(e)}"