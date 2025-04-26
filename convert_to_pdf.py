import os
from pathlib import Path
from fpdf import FPDF

def text_to_pdf(input_file, output_file):
    """Convert a text file to PDF."""
    # Create instance of FPDF class
    pdf = FPDF()
    pdf.add_page()
    
    # Set font and style
    pdf.set_font("Arial", size=12)
    
    # Read text file
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            # Add text to PDF
            pdf.cell(200, 10, txt=line.strip(), ln=True)
    
    # Save the PDF
    pdf.output(output_file)
    print(f"Created PDF: {output_file}")

def main():
    # Path to the sample documents
    sample_dir = Path("sample_docs")
    
    # Create pdfs directory inside sample_docs if it doesn't exist
    pdf_dir = sample_dir / "pdfs"
    pdf_dir.mkdir(exist_ok=True)
    
    # Convert each text file to PDF
    for txt_file in sample_dir.glob("*.txt"):
        pdf_file = pdf_dir / f"{txt_file.stem}.pdf"
        try:
            text_to_pdf(txt_file, pdf_file)
        except Exception as e:
            print(f"Error converting {txt_file.name}: {e}")

if __name__ == "__main__":
    main() 