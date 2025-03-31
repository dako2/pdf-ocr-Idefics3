from pdf2image import convert_from_path
from pytesseract import image_to_string
import os

def extract_chinese_text_ocr(pdf_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print("Converting PDF to images...")
    pages = convert_from_path(pdf_path, dpi=300)

    full_text = ""
    for i, page in enumerate(pages):
        print(f"OCR on page {i+1}...")
        text = image_to_string(page, lang='chi_sim')  # Simplified Chinese
        full_text += f"\n\n--- Page {i+1} ---\n{text}"
        with open(os.path.join(output_folder, f"page{i+1}.txt"), "w", encoding="utf-8") as f:
            f.write(text)

    with open(os.path.join(output_folder, "full_text.txt"), "w", encoding="utf-8") as f:
        f.write(full_text)

    print("✅ OCR text extraction complete!")

# Example usage
if __name__ == "__main__":
    pdf_path = "/Users/dako22/Downloads/高等院校理工科教材化学史教程第三版电子书.pdf"         # Replace with your PDF file path
    output_folder = "ocr_output"
    
    extract_chinese_text_ocr(pdf_path, output_folder)
 