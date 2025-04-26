import os
import streamlit as st
import pandas as pd
import numpy as np
import cv2
from PIL import Image
import tempfile
import json
from pathlib import Path

from ocr_utils import extract_text_from_file, extract_loan_details, extract_table_data
from preprocessing import process_image_for_ocr, convert_pdf_to_images

# Set page configuration
st.set_page_config(
    page_title="Loan Document Processor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Directory for sample documents
SAMPLE_DOCS_DIR = Path("sample_docs")

def save_uploaded_file(uploaded_file):
    """Save the uploaded file to a temporary location and return the path."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        tmp.write(uploaded_file.getvalue())
        return tmp.name

def display_extracted_info(extracted_info):
    """Display extracted information in a formatted way."""
    if not extracted_info:
        st.warning("No information could be extracted from the document.")
        return
    
    # Create three columns
    col1, col2, col3 = st.columns(3)
    
    # Column 1: Loan Details
    with col1:
        st.subheader("Loan Details")
        if 'loan_amount' in extracted_info:
            st.metric("Loan Amount", f"${extracted_info['loan_amount']}")
        if 'interest_rate' in extracted_info:
            st.metric("Interest Rate", f"{extracted_info['interest_rate']}%")
        if 'loan_term' in extracted_info:
            st.metric("Loan Term", extracted_info['loan_term'])
        if 'loan_type' in extracted_info:
            st.metric("Loan Type", extracted_info['loan_type'])
    
    # Column 2: Borrower Information
    with col2:
        st.subheader("Borrower Information")
        if 'borrower_name' in extracted_info:
            st.text_input("Borrower", value=extracted_info['borrower_name'], disabled=True)
        if 'borrower_address' in extracted_info:
            st.text_area("Address", value=extracted_info['borrower_address'], height=100, disabled=True)
        if 'borrower_phone' in extracted_info:
            st.text_input("Phone", value=extracted_info['borrower_phone'], disabled=True)
        if 'borrower_email' in extracted_info:
            st.text_input("Email", value=extracted_info['borrower_email'], disabled=True)
    
    # Column 3: Additional Information
    with col3:
        st.subheader("Additional Details")
        if 'application_date' in extracted_info:
            st.text_input("Application Date", value=extracted_info['application_date'], disabled=True)
        if 'lender_name' in extracted_info:
            st.text_input("Lender", value=extracted_info['lender_name'], disabled=True)
        if 'social_security' in extracted_info:
            st.text_input("SSN", value=extracted_info['social_security'], disabled=True)
        if 'collateral' in extracted_info:
            st.text_area("Collateral", value=extracted_info['collateral'], height=100, disabled=True)
    
    # Add edit button for each field
    st.subheader("Edit Extracted Information")
    
    edited_info = {}
    for field, value in extracted_info.items():
        # Create a more human-readable field name
        field_name = field.replace('_', ' ').title()
        
        # For longer text like address, use text_area
        if field in ['borrower_address', 'collateral']:
            edited_info[field] = st.text_area(f"Edit {field_name}", value=value)
        else:
            edited_info[field] = st.text_input(f"Edit {field_name}", value=value)
    
    # Add button to save edits
    if st.button("Save Edits"):
        st.success("Information updated successfully!")
        # In a real app, you would save this information to a database or file
        return edited_info
    
    return extracted_info

def process_document(file_path):
    """Process document to extract text and information."""
    with st.spinner("Processing document..."):
        # Extract text from the document
        extracted_text = extract_text_from_file(file_path)
        
        # Extract structured information
        extracted_info = extract_loan_details(extracted_text)
        
        return extracted_text, extracted_info

def main():
    """Main function to run the Streamlit app."""
    st.title("Personal Loan Document Processor")
    st.markdown("""
    Upload loan documents to extract key information using OCR technology.
    The app supports PDF and image files (JPG, PNG, TIFF).
    """)
    
    # Sidebar for navigation and settings
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio(
        "Select Mode",
        ["Upload Document", "Sample Documents", "Settings"]
    )
    
    if app_mode == "Upload Document":
        st.header("Upload a Loan Document")
        
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg", "tiff", "txt"])
        
        if uploaded_file is not None:
            # Display file details
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.2f} KB"
            }
            st.write("File Details:", file_details)
            
            # Save the uploaded file temporarily
            temp_file_path = save_uploaded_file(uploaded_file)
            
            # Add a button to process the document
            if st.button("Process Document"):
                # Process the document
                extracted_text, extracted_info = process_document(temp_file_path)
                
                # Display tabs for different views
                tab1, tab2, tab3 = st.tabs(["Extracted Information", "Raw Text", "Document Image"])
                
                with tab1:
                    display_extracted_info(extracted_info)
                
                with tab2:
                    st.subheader("Extracted Raw Text")
                    st.text_area("Text", extracted_text, height=400)
                
                with tab3:
                    st.subheader("Document Preview")
                    # Display the document (first page if PDF)
                    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                    if file_ext == '.pdf':
                        images = convert_pdf_to_images(temp_file_path)
                        st.image(images[0], caption="First Page", use_column_width=True)
                    elif file_ext in ['.png', '.jpg', '.jpeg', '.tiff']:
                        st.image(Image.open(temp_file_path), caption="Document Image", use_column_width=True)
                    elif file_ext == '.txt':
                        with st.expander("Text File Content", expanded=True):
                            with open(temp_file_path, 'r') as f:
                                st.code(f.read())
            
            # Clean up the temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    elif app_mode == "Sample Documents":
        st.header("Sample Documents")
        
        # Check if sample docs directory exists
        if not SAMPLE_DOCS_DIR.exists():
            st.warning(f"Sample documents directory ({SAMPLE_DOCS_DIR}) not found.")
            if st.button("Create Sample Documents Directory"):
                SAMPLE_DOCS_DIR.mkdir(exist_ok=True)
                st.success(f"Created directory: {SAMPLE_DOCS_DIR}")
                st.info("Please add sample documents to this directory.")
            return
        
        # List sample documents
        sample_files = list(SAMPLE_DOCS_DIR.glob("*.*"))
        if not sample_files:
            st.info("No sample documents found. Please add some documents to the sample_docs directory.")
            return
        
        # Display sample documents in a selectbox
        selected_file = st.selectbox(
            "Select a sample document",
            options=sample_files,
            format_func=lambda x: x.name
        )
        
        if selected_file:
            st.write(f"Selected: {selected_file.name}")
            
            # Display a preview of the document
            file_ext = selected_file.suffix.lower()
            if file_ext == '.pdf':
                try:
                    images = convert_pdf_to_images(selected_file)
                    st.image(images[0], caption="First Page", use_column_width=True)
                except Exception as e:
                    st.error(f"Error loading PDF: {e}")
            elif file_ext in ['.png', '.jpg', '.jpeg', '.tiff']:
                try:
                    st.image(Image.open(selected_file), caption="Document Image", use_column_width=True)
                except Exception as e:
                    st.error(f"Error loading image: {e}")
            elif file_ext == '.txt':
                with st.expander("Text File Content", expanded=True):
                    try:
                        with open(selected_file, 'r') as f:
                            st.code(f.read())
                    except Exception as e:
                        st.error(f"Error loading text file: {e}")
            
            # Add a button to process the document
            if st.button("Process Sample Document"):
                # Process the document
                extracted_text, extracted_info = process_document(selected_file)
                
                # Display tabs for different views
                tab1, tab2 = st.tabs(["Extracted Information", "Raw Text"])
                
                with tab1:
                    display_extracted_info(extracted_info)
                
                with tab2:
                    st.subheader("Extracted Raw Text")
                    st.text_area("Text", extracted_text, height=400)
    
    elif app_mode == "Settings":
        st.header("Settings")
        
        # OCR Settings
        st.subheader("OCR Settings")
        
        # Create columns for settings
        col1, col2 = st.columns(2)
        
        with col1:
            # Threshold type
            threshold_type = st.selectbox(
                "Thresholding Method",
                options=["adaptive", "otsu", "binary"],
                index=0
            )
            
            # Denoise strength
            denoise_strength = st.slider(
                "Denoising Strength",
                min_value=1,
                max_value=20,
                value=10
            )
        
        with col2:
            # Image resize
            resize_width = st.number_input(
                "Resize Width (pixels)",
                min_value=800,
                max_value=3000,
                value=1700,
                step=100
            )
            
            # OCR engine mode
            ocr_engine_mode = st.selectbox(
                "OCR Engine Mode",
                options=["1 - Legacy engine only", "2 - Neural nets LSTM engine only", "3 - Default, based on what is available"],
                index=2,
                format_func=lambda x: x
            )
        
        # Save settings button
        if st.button("Save Settings"):
            settings = {
                "threshold_type": threshold_type,
                "denoise_strength": denoise_strength,
                "resize_width": resize_width,
                "ocr_engine_mode": ocr_engine_mode.split(" - ")[0]
            }
            
            # In a real app, you would save these settings to a file or database
            st.success("Settings saved successfully!")
            st.json(settings)

if __name__ == "__main__":
    main() 