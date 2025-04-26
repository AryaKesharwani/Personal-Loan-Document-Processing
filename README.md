# Personal Loan Document Processing

A Streamlit application for extracting and processing information from personal loan documents using OCR (Optical Character Recognition).

## Features

- **Document Upload**: Upload loan documents in PDF or image formats (JPG, PNG, TIFF)
- **OCR Processing**: Extract text content from documents
- **Information Extraction**: Automatically identify and extract key loan information
- **Data Visualization**: View and edit extracted information in a user-friendly interface
- **Preprocessing**: Enhance document quality for better OCR results
- **Sample Documents**: Process sample loan documents included with the application

## Technologies Used

- **Streamlit**: Web application framework
- **OpenCV**: Image processing and enhancement
- **Tesseract OCR**: Optical character recognition
- **Pandas**: Data manipulation
- **PDF2Image**: PDF conversion

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/Personal-Loan-Document-Processing.git
   cd Personal-Loan-Document-Processing
   ```

2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install Tesseract OCR:
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`
   - **Windows**: Download installer from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

5. For PDF processing, install poppler:
   - **Ubuntu/Debian**: `sudo apt-get install poppler-utils`
   - **macOS**: `brew install poppler`
   - **Windows**: Download from [poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)

## Usage

1. Start the application:
   ```
   streamlit run app.py
   ```

2. Access the application in your web browser (usually at http://localhost:8501)

3. Upload a loan document or select from the sample documents

4. Process the document to extract information

5. View and edit the extracted information as needed

## Project Structure

- `app.py`: Main Streamlit application
- `ocr_utils.py`: OCR and data extraction functions
- `preprocessing.py`: Image preprocessing functions
- `sample_docs/`: Directory containing sample loan documents
- `requirements.txt`: List of Python dependencies
- `README.md`: Project documentation

## Supported Document Types

- Loan Applications
- Loan Agreements
- Promissory Notes
- Amortization Schedules
- Mortgage Documents
- Personal Loan Contracts

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 