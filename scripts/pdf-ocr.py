from pdf2image import convert_from_path
import pytesseract
import os

def ocr_pdf_pages(pdf_path, output_folder, dpi=300):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pages = convert_from_path(pdf_path, dpi=dpi)
    results = []

    for i, page in enumerate(pages):
        image_path = os.path.join(output_folder, f"page_{i+1}.png")
        page.save(image_path, "PNG")

        # OCR on the image
        text = pytesseract.image_to_string(page, lang='chi_sim')  # for Chinese
        text_file = os.path.splitext(image_path)[0] + ".txt"

        with open(text_file, "w", encoding="utf-8") as f:
            f.write(text)

        results.append({"page": i+1, "image_path": image_path, "text_path": text_file})

    return results

# Example usage
if __name__ == "__main__":
    pdf_path = "/Users/dako22/Downloads/高等院校理工科教材化学史教程第三版电子书.pdf"         # Replace with your PDF file path
    output_folder = "ocr_output"
    ocr_results = ocr_pdf_pages(pdf_path, output_folder)

    for result in ocr_results[:3]:  # show first few pages
        print(f"Page {result['page']}: Image - {result['image_path']}, Text - {result['text_path']}")
