from pypdf import PdfReader
import os

PDF_PATH = r"c:\DesarrolloWeb\nomenclador\rimac\fweiofewiofweifwe.pdf"

def check_images():
    if not os.path.exists(PDF_PATH):
        print(f"File not found: {PDF_PATH}")
        return

    try:
        reader = PdfReader(PDF_PATH)
        page = reader.pages[0]
        
        count = 0
        for image_file_object in page.images:
            print(f"Found image: {image_file_object.name}, size: {len(image_file_object.data)} bytes")
            count += 1
            
        if count > 0:
            print(f"Success: Found {count} images on the first page.")
        else:
            print("No images found on the first page via pypdf.")
            
    except Exception as e:
        print(f"Error checking images: {e}")

if __name__ == "__main__":
    check_images()
