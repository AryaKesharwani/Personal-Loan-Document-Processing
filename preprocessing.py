import cv2
import numpy as np
from skimage import filters
from PIL import Image

def resize_image(image, width=1700):
    """Resize image while maintaining aspect ratio."""
    h, w = image.shape[:2]
    ratio = width / w
    return cv2.resize(image, (width, int(h * ratio)))

def convert_to_grayscale(image):
    """Convert image to grayscale."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def apply_threshold(image, threshold_type="adaptive"):
    """Apply thresholding to improve OCR accuracy.
    
    Args:
        image: Grayscale image
        threshold_type: Type of thresholding ("adaptive", "otsu", "binary")
    """
    if threshold_type == "adaptive":
        return cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
    elif threshold_type == "otsu":
        _, thresholded = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresholded
    else:  # binary
        _, thresholded = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
        return thresholded

def denoise_image(image):
    """Remove noise from the image."""
    return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)

def deskew_image(image):
    """Correct the skew in a document image."""
    # Calculate skew angle
    gray = image.copy() if len(image.shape) == 2 else convert_to_grayscale(image)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
    
    if lines is None or len(lines) == 0:
        return image
    
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x2 - x1 == 0:  # Avoid division by zero
            continue
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        if -45 < angle < 45:  # Filter out vertical lines
            angles.append(angle)
    
    if not angles:
        return image
    
    # Calculate median angle
    median_angle = np.median(angles)
    
    # Rotate image to correct skew
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

def enhance_image(image):
    """Enhance image for better OCR using multiple techniques."""
    # Resize image
    image = resize_image(image)
    
    # Convert to grayscale if not already
    if len(image.shape) == 3:
        gray = convert_to_grayscale(image)
    else:
        gray = image.copy()
    
    # Denoise
    denoised = denoise_image(gray)
    
    # Deskew
    deskewed = deskew_image(denoised)
    
    # Apply threshold
    thresholded = apply_threshold(deskewed, "adaptive")
    
    return thresholded

def process_image_for_ocr(image_path):
    """Process an image for optimal OCR performance."""
    # Read image
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Could not read image at {image_path}")
    
    # Apply all enhancements
    processed = enhance_image(image)
    
    return processed

def convert_pdf_to_images(pdf_path):
    """Convert PDF to images using pdf2image library."""
    try:
        from pdf2image import convert_from_path
        return convert_from_path(pdf_path, dpi=300)
    except ImportError:
        raise ImportError("pdf2image is required. Install it with: pip install pdf2image") 