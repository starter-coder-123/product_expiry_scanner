# Product Expiry Date Scanner

A full-stack web application that allows users to scan product labels using their device camera to check if the product has expired. The application supports both barcodes and QR codes and uses OCR to extract and validate expiry dates.

---

## Features
- Welcome page with a "Get Started" button.
- Camera access for scanning product labels.
- Real-time processing of expiry dates in different formats (e.g., `Dec 2024`, `12/2024`).
- User feedback:
  - **Expired products**: Sad emoji with a red background.
  - **Valid products**: Smiley emoji with a green background.

---

## Technologies Used
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask framework)
- **OCR Library**: Tesseract
- **Image Processing**: PIL (Python Imaging Library)
- **Date Parsing**: Python's `datetime` and `re`

---

## Prerequisites
- Python 3.8 or higher
- Tesseract OCR installed (ensure it's added to the system PATH)
- pip (Python package manager)

---

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/product-expiry-scanner.git
   cd product-expiry-scanner
