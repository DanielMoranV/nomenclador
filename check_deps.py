import shutil
import os
import sys

def check_dependencies():
    print(f"Python: {sys.version}")
    
    try:
        import pytesseract
        print("pytesseract: Installed")
    except ImportError:
        print("pytesseract: Not installed")

    try:
        import pdf2image
        print("pdf2image: Installed")
    except ImportError:
        print("pdf2image: Not installed")
        
    tesseract_cmd = shutil.which("tesseract")
    if tesseract_cmd:
        print(f"Tesseract found at: {tesseract_cmd}")
    else:
        # Check common windows paths
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\siste\AppData\Local\Tesseract-OCR\tesseract.exe"
        ]
        found = False
        for path in common_paths:
            if os.path.exists(path):
                print(f"Tesseract found at: {path}")
                found = True
                break
        if not found:
            print("Tesseract not found in PATH or common locations")

if __name__ == "__main__":
    check_dependencies()
