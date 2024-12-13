# File: test_app.py
import unittest
from app import preprocess_image, decode_image, extract_expiry_date
from PIL import Image
import base64
import io
import datetime  # Ensure this is imported for datetime.datetime usage

class TestAppFunctions(unittest.TestCase):

    def test_preprocess_image(self):
        # Create a dummy image for preprocessing
        image = Image.new('RGB', (100, 100), color='white')
        processed_image = preprocess_image(image)
        self.assertIsInstance(processed_image, Image.Image)

    def test_decode_image(self):
        # Create a test base64-encoded image
        img = Image.new('RGB', (100, 100), color='white')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        base64_img = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
        decoded_image = decode_image(base64_img)
        self.assertIsInstance(decoded_image, Image.Image)

    def test_extract_expiry_date(self):
        # Test various date formats
        text = "12/2024"
        date = extract_expiry_date(text)
        self.assertEqual(date, datetime.datetime(2024, 12, 31))

        text = "31/12/2024"
        date = extract_expiry_date(text)
        self.assertEqual(date, datetime.datetime(2024, 12, 31))

        text = "Dec 2024"
        date = extract_expiry_date(text)
        self.assertEqual(date, datetime.datetime(2024, 12, 31))

if __name__ == "__main__":
    unittest.main()
