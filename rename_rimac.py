import os
import re
import sys
import shutil
import io
from pypdf import PdfReader
from PIL import Image

try:
    import pytesseract
except ImportError:
    pytesseract = None

# Configuration
PDF_PATH = r"c:\DesarrolloWeb\nomenclador\rimac\fweiofewiofweifwe.pdf"

def extract_text_from_images(path):
    if not pytesseract:
        print("pytesseract not imported.")
        return ""
        
    # Check for Tesseract executable
    tesseract_cmd = shutil.which("tesseract")
    if not tesseract_cmd:
        # Try common windows paths
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\siste\AppData\Local\Tesseract-OCR\tesseract.exe"
        ]
        for p in common_paths:
            if os.path.exists(p):
                pytesseract.pytesseract.tesseract_cmd = p
                print(f"Using Tesseract at: {p}")
                break
    
    reader = PdfReader(path)
    if len(reader.pages) == 0:
        return ""
        
    page = reader.pages[0]
    text_content = ""
    
    # Extract images using pypdf
    if page.images:
        print(f"Found {len(page.images)} images on page 1. Performing OCR...")
        for image_file_object in page.images:
            try:
                # pypdf image object has .data which is bytes
                image_data = image_file_object.data
                image = Image.open(io.BytesIO(image_data))
                
                # Perform OCR
                text = pytesseract.image_to_string(image)
                text_content += text + "\n"
            except Exception as e:
                print(f"Error processing image {image_file_object.name}: {e}")
    else:
        print("No images found on the first page via pypdf.")
        
    return text_content

def find_invoice_data(text):
    print("--- Extracted Text Preview ---")
    print(text[:500])
    print("------------------------------")

    # Pattern: Series (4 chars, usually start with F or B) followed by dash/space and 8 digits
    # Example: F004- 00030216
    
    # Regex 1: Explicit Series-Number pattern
    # Looks for 4 alphanumeric chars (Series) + separators + 8 digits (Number)
    match = re.search(r"\b([A-Za-z0-9]{4})[-\s]+(\d{8})\b", text)
    if match:
        return match.group(1).upper(), match.group(2)

    # Regex 2: Look for "Factura" or "Serie" context
    # Example: "Factura F004-12345678"
    match = re.search(r"Factura.*?([A-Za-z0-9]{4}).*?(\d{8})", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).upper(), match.group(2)
        
    return None, None

def process_file(file_path, output_dir):
    filename = os.path.basename(file_path)
    print(f"\nProcessing: {filename}")
    
    # Try extracting textual content first (in case some are native PDFs)
    try:
        reader = PdfReader(file_path)
        text = reader.pages[0].extract_text()
    except:
        text = ""

    # If text is too short, try OCR
    if not text or len(text.strip()) < 10:
        print("  Text empty or too short. Attempting OCR...")
        ocr_text = extract_text_from_images(file_path)
        if ocr_text:
            text += "\n" + ocr_text

    series, number = find_invoice_data(text)

    if series and number:
        print(f"  > Found: Series={series}, Number={number}")
        
        # New name format: 20526109237_01_[SERIE]_[NUMERO].pdf
        new_name = f"20526109237_01_{series}_{number}.pdf"
        new_path = os.path.join(output_dir, new_name)
        
        print(f"  > Saving to: {new_path}")
        try:
           # Copy instead of rename to preserve original during testing, 
           # or move if desired. User said "create a folder out where renamed pdfs are".
           # Usually implies copy or move. I will COPY to be safe, or just write.
           shutil.copy2(file_path, new_path)
           print("  > Success!")
        except Exception as e:
           print(f"  > Error saving file: {e}")
            
    else:
        print("  > Could NOT identify Series and Invoice Number.")
        # Optionally copy to an 'error' folder or just skip
        error_path = os.path.join(output_dir, f"ERROR_{filename}")
        try:
            shutil.copy2(file_path, error_path)
            print(f"  > Copied to {error_path} for manual review.")
        except:
             pass

def main():
    SOURCE_DIR = r"c:\DesarrolloWeb\nomenclador\rimac"
    OUTPUT_DIR = os.path.join(SOURCE_DIR, "out")
    
    if not os.path.exists(SOURCE_DIR):
        print(f"Source directory not found: {SOURCE_DIR}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

    files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith('.pdf')]
    
    print(f"Found {len(files)} PDF files in {SOURCE_DIR}...")
    
    for f in files:
        file_path = os.path.join(SOURCE_DIR, f)
        process_file(file_path, OUTPUT_DIR)
        
    print("\nBatch processing complete.")

if __name__ == "__main__":
    main()
