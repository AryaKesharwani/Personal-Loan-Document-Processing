import os
import re
import pytesseract
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from preprocessing import process_image_for_ocr, convert_pdf_to_images

def perform_ocr(image):
    """
    Perform OCR on the processed image using pytesseract.
    
    Args:
        image: Processed image ready for OCR
        
    Returns:
        Extracted text as a string
    """
    if isinstance(image, np.ndarray):
        # Convert OpenCV image to PIL format
        image = Image.fromarray(image)
    
    # Configure pytesseract parameters for better results
    custom_config = r'--oem 3 --psm 6'
    
    # Perform OCR
    text = pytesseract.image_to_string(image, config=custom_config)
    
    return text

def extract_text_from_file(file_path):
    """
    Extract text from an image, PDF file, or text file.
    
    Args:
        file_path: Path to the image, PDF, or text file
        
    Returns:
        Extracted text as a string
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Handle text files directly
    if file_ext in ['.txt', '.text']:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise ValueError(f"Error reading text file: {e}")
    
    elif file_ext == '.pdf':
        # Convert PDF to images
        images = convert_pdf_to_images(file_path)
        
        # Process each page and perform OCR
        texts = []
        for img in images:
            # Convert PIL image to OpenCV format
            open_cv_image = np.array(img) 
            # Convert RGB to BGR (OpenCV format)
            open_cv_image = open_cv_image[:, :, ::-1].copy() 
            
            processed_img = process_image_for_ocr(open_cv_image)
            texts.append(perform_ocr(processed_img))
        
        return "\n\n".join(texts)
    else:
        # Process single image file
        processed_img = process_image_for_ocr(file_path)
        return perform_ocr(processed_img)

# Extraction patterns for common loan document fields
PATTERNS = {
    'loan_amount': r'loan amount[:\s]*[$]?([0-9,\.]+)',
    'interest_rate': r'interest rate[:\s]*([0-9\.]+)[%]?',
    'loan_term': r'loan term[:\s]*([0-9]+)\s+(years|months)',
    'loan_type': r'loan type[:\s]*([A-Za-z\s]+)',
    'borrower_name': r'borrower(?:\'s)?\s+name[:\s]*([A-Za-z\s]+)',
    'borrower_address': r'(?:address|residence)[:\s]*([A-Za-z0-9\s\.,#-]+)',
    'borrower_phone': r'(?:phone|telephone)[:\s]*\(?([0-9]{3})\)?[\s.-]?([0-9]{3})[\s.-]?([0-9]{4})',
    'borrower_email': r'email[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
    'social_security': r'(?:SSN|social security)[:\s]*([0-9]{3})-?([0-9]{2})-?([0-9]{4})',
    'application_date': r'(?:application|date)[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
    'lender_name': r'lender[:\s]*([A-Za-z\s]+)',
    'collateral': r'collateral[:\s]*([A-Za-z0-9\s\.,#-]+)'
}

def clean_extracted_value(value):
    """Clean extracted values from OCR text."""
    if value is None:
        return None
    
    # Remove extra whitespace
    value = re.sub(r'\s+', ' ', value).strip()
    
    # Replace common OCR errors
    value = value.replace('l', '1')
    value = value.replace('O', '0')
    
    return value

def extract_loan_details(text):
    """
    Extract loan details from OCR text using regex patterns.
    
    Args:
        text: OCR extracted text
        
    Returns:
        Dictionary of extracted loan details
    """
    # Standardize text for easier pattern matching
    text = text.lower()
    
    # Dict to store the extracted information
    extracted_info = {}
    
    # Apply each pattern and extract information
    for field, pattern in PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if field == 'borrower_phone':
                # Format phone number
                extracted_info[field] = f"({match.group(1)}) {match.group(2)}-{match.group(3)}"
            elif field == 'social_security':
                # Format SSN
                extracted_info[field] = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
            elif field == 'loan_term':
                # Combine term number and unit
                extracted_info[field] = f"{match.group(1)} {match.group(2)}"
            else:
                extracted_info[field] = match.group(1)
                
            # Clean extracted value
            extracted_info[field] = clean_extracted_value(extracted_info[field])
    
    return extracted_info

def extract_table_data(image, table_area=None):
    """
    Extract tabular data from document images.
    
    Args:
        image: Image containing table
        table_area: Optional bounding box of table area (x, y, width, height)
        
    Returns:
        DataFrame with extracted table data
    """
    # If table area is specified, crop the image
    if table_area is not None:
        x, y, w, h = table_area
        image = image[y:y+h, x:x+w]
    
    # Process image for better OCR results
    processed = process_image_for_ocr(image)
    
    # Use pytesseract to extract table data
    table_data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DATAFRAME)
    
    # Filter out rows with low confidence
    table_data = table_data[table_data['conf'] > 50]
    
    # Group by line number
    lines = {}
    for _, row in table_data.iterrows():
        if row['text'].strip():
            if row['block_num'] not in lines:
                lines[row['block_num']] = []
            lines[row['block_num']].append(row['text'])
    
    # Create DataFrame from extracted lines
    rows = []
    for _, line in lines.items():
        if line:  # Skip empty lines
            rows.append(line)
    
    # Create DataFrame (handling varying column counts)
    max_cols = max(len(row) for row in rows) if rows else 0
    for i, row in enumerate(rows):
        while len(row) < max_cols:
            row.append('')
    
    df = pd.DataFrame(rows)
    
    return df 