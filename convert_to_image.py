import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap

def text_to_image(input_file, output_file):
    """Convert a text file to an image."""
    # Read text file
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Create a white background image
    width, height = 1700, 2200
    background_color = (255, 255, 255)
    text_color = (0, 0, 0)
    
    image = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(image)
    
    # Use default font if Arial not available
    try:
        font = ImageFont.truetype("Arial", 24)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw the text on the image
    margin = 50
    offset = margin
    
    # Wrap text to fit width
    wrapper = textwrap.TextWrapper(width=80)
    word_list = wrapper.wrap(text)
    
    for line in word_list:
        draw.text((margin, offset), line, font=font, fill=text_color)
        offset += font.getbbox(line)[3] + 10
        
        if offset > height - margin:
            # If we run out of space, stop
            break
    
    # Save the image
    image.save(output_file)
    print(f"Created image: {output_file}")

def main():
    # Path to the sample documents
    sample_dir = Path("sample_docs")
    
    # Create images directory inside sample_docs if it doesn't exist
    img_dir = sample_dir / "images"
    img_dir.mkdir(exist_ok=True)
    
    # Convert each text file to an image
    for txt_file in sample_dir.glob("*.txt"):
        img_file = img_dir / f"{txt_file.stem}.png"
        try:
            text_to_image(txt_file, img_file)
        except Exception as e:
            print(f"Error converting {txt_file.name}: {e}")

if __name__ == "__main__":
    main() 