# File: app.py
from flask import Flask, render_template, request, jsonify
import base64
import io
from PIL import Image
import pytesseract
import datetime
import re
from calendar import monthrange
import cv2
import numpy as np
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

def preprocess_image(image):
    """Preprocess the image to improve OCR accuracy."""
    image = image.convert('L')  # Convert to grayscale
    image_np = np.array(image)
    # Apply Gaussian blur and adaptive thresholding
    image_np = cv2.GaussianBlur(image_np, (5, 5), 0)
    image_np = cv2.adaptiveThreshold(image_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return Image.fromarray(image_np)

def decode_image(image_data):
    """Decode the base64 image and return a preprocessed PIL image."""
    try:
        # Handle cases where the base64 data may not have a prefix
        if "," in image_data:
            image_data = image_data.split(",")[1]
        image_data = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_data))
        return preprocess_image(image)
    except Exception as e:
        logging.error(f"Failed to decode image: {e}")
        raise ValueError("Image decoding failed. Ensure the image data is properly formatted.") from e

def clean_ocr_text(text):
    """Clean common OCR misinterpretations."""
    text = text.replace("O", "0").replace("l", "1").strip()
    logging.debug(f"Cleaned OCR text: {text}")
    return text

def extract_expiry_date(text):
    """Extract the expiry date from OCR text and return it as a datetime object."""
    try:
        if not text:
            logging.warning("No text detected by OCR.")
            return None

        # Normalize the text for better matching
        text = text.replace(' ', '').replace('-', '/').upper()
        text = " ".join(text.splitlines())
        logging.debug(f"Normalized OCR text for date extraction: {text}")

        # Extended patterns to support various formats
        date_patterns = [
            r'([A-Za-z]+)\s*(\d{4})',        # Month name and year (e.g., Dec 2024)
            r'(\d{2})[-/](\d{4})',           # MM/YYYY or MM-YYYY (e.g., 12/2024)
            r'(\d{2})/(\d{2})/(\d{4})'       # dd/MM/YYYY (e.g., 31/12/2024)
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 2:  # For "Month Year" or "MM/YYYY"
                    if match[1].isalpha():
                        # Handle month name (both short and full)
                        try:
                            month = datetime.datetime.strptime(match[1], "%b").month
                        except ValueError:
                            month = datetime.datetime.strptime(match[1], "%B").month
                        year = int(match[2])
                    else:
                        month, year = map(int, (match[1], match[2]))
                    last_day = monthrange(year, month)[1]
                    return datetime.datetime(year, month, last_day)

                elif len(match.groups()) == 3:  # For "dd/MM/YYYY"
                    day, month, year = map(int, (match[1], match[2], match[3]))
                    return datetime.datetime(year, month, day)

        logging.warning(f"No valid expiry date found in the text: {text}")
        return None
    except Exception as e:
        logging.error(f"Date extraction error: {e}")
        return None

def compare_expiry_date(expiry_date):
    """Compare the expiry date with the current date."""
    if not expiry_date:
        logging.warning("Expiry date is None; cannot compare.")
        return False
    live_date = datetime.datetime.now()
    return live_date > expiry_date

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"error": "No image data provided"}), 400

        # Decode and preprocess the image
        image = decode_image(data['image'])

        # Perform OCR and clean the text
        ocr_result = pytesseract.image_to_string(image, config='--psm 6 --oem 3')
        logging.debug(f"Raw OCR Output: {ocr_result}")
        ocr_result = clean_ocr_text(ocr_result)

        # Extract expiry date
        expiry_date = extract_expiry_date(ocr_result)
        if not expiry_date:
            return jsonify({"error": "No expiry date found in image."}), 400

        # Compare expiry date with the current date
        is_expired = compare_expiry_date(expiry_date)
        return jsonify({"isExpired": is_expired})

    except Exception as e:
        logging.error(f"Error during processing: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
