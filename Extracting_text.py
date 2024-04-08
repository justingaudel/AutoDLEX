from flask import Flask, request, render_template
from PIL import Image
import numpy as np
import io
import cv2
import pytesseract 

app = Flask(__name__)

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_image(img):
    # Convert the image to grayscale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur to reduce noise
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 0)

    # Apply adaptive thresholding
    img_thresh = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    return img_thresh

@app.route('/')
def index():
    return render_template('camera.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        if 'image' not in request.files:
            return "No image provided"

        # Read the image file sent from the frontend
        image_data = request.files['image'].read()

        # Convert the image bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))

        # Convert the image to OpenCV format
        img_cv = np.array(image)

        # Preprocess the image
        img_processed = preprocess_image(img_cv)

        # Perform OCR
        extracted_text = pytesseract.image_to_string(img_processed)

        return extracted_text
        
    except Exception as e:
        return f"Error processing image: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
