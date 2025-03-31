import os
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox, LTTextLine, LTImage

def save_image_and_caption(lt_image, caption, output_folder, page_num, image_index):
    if not caption or not lt_image.stream:
        return None  # Skip if no caption

    try:
        image_data = lt_image.stream.get_data()
    except Exception as e:
        print(f"Error extracting image data: {e}")
        return None

    ext = 'png'
    base_name = f"page{page_num}_img{image_index}"
    image_path = os.path.join(output_folder, f"{base_name}.{ext}")
    caption_path = os.path.join(output_folder, f"{base_name}.txt")

    with open(image_path, "wb") as f:
        f.write(image_data)

    with open(caption_path, "w", encoding="utf-8") as f:
        f.write(caption.strip())

    return image_path

def extract_figures_with_captions(pdf_path, output_folder, caption_threshold=10):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    results = []

    for page_index, layout in enumerate(extract_pages(pdf_path), start=1):
        images = []
        texts = []

        def parse_layout(obj):
            if isinstance(obj, LTImage):
                images.append(obj)
            elif isinstance(obj, (LTTextBox, LTTextLine)):
                texts.append(obj)
            elif hasattr(obj, "_objs"):
                for child in obj._objs:
                    parse_layout(child)

        parse_layout(layout)

        for i, img in enumerate(images, start=1):
            img_bbox = img.bbox
            caption_lines = []

            for text in texts:
                text_bbox = text.bbox
                vertical_gap = img_bbox[1] - text_bbox[3]

                if 0 <= vertical_gap <= caption_threshold:
                    overlap = max(0, min(img_bbox[2], text_bbox[2]) - max(img_bbox[0], text_bbox[0]))
                    img_width = img_bbox[2] - img_bbox[0]
                    if img_width > 0 and (overlap / img_width) > 0.3:
                        caption_lines.append(text.get_text().strip())

            caption = " ".join(caption_lines)

            # Save image only if caption exists
            image_path = save_image_and_caption(img, caption, output_folder, page_index, i)
            if image_path:
                results.append({
                    "page": page_index,
                    "image_path": image_path,
                    "caption": caption
                })

    return results

def extract_all_text_from_pdf(pdf_path):
    """
    Extracts all text from the PDF file, page by page.
    
    Returns:
        dict[int, str]: Mapping from page number to text content.
    """
    all_text = {}

    for page_index, layout in enumerate(extract_pages(pdf_path), start=1):
        page_text = []

        for element in layout:
            if isinstance(element, (LTTextBox, LTTextLine)):
                page_text.append(element.get_text())

        all_text[page_index] = "".join(page_text).strip()

    return all_text

# Example usage
if __name__ == "__main__":
    output_folder = "高"  # Replace with your desired output folder
    pdf_path = "/Users/dako22/Downloads/高等院校理工科教材化学史教程第三版电子书.pdf"         # Replace with your PDF file path

    # 1. Extract figures with captions
    results = extract_figures_with_captions(pdf_path, output_folder)
    for r in results:
        print(f"[Page {r['page']}] Image saved at: {r['image_path']}")
        print(f"Caption: {r['caption']}\n")

    # 2. Extract all text
    full_text = extract_all_text_from_pdf(pdf_path)
    for page_num, text in full_text.items():
        print(f"\n===== Page {page_num} =====\n{text[:500]}...")  # Preview first 500 chars
