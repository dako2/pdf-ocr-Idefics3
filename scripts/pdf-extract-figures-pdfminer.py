import os
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox, LTTextLine, LTImage

def save_image_and_caption(lt_image, caption, output_folder, page_num, image_index):
    """
    Saves the image and its caption (as a .txt file) if caption is not empty.
    """
    if not caption or not lt_image.stream:
        return None  # Skip saving if no caption

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

            # Save image and caption only if caption exists
            image_path = save_image_and_caption(img, caption, output_folder, page_index, i)
            if image_path:
                results.append({
                    "page": page_index,
                    "image_path": image_path,
                    "caption": caption
                })

    return results

# Example usage:
if __name__ == "__main__":
    output_folder = "figures_with_captions"   
    pdf_path = "The History of Chemistry by John Hudson (auth.) (z-lib.org) (1).pdf"         # Replace with your PDF file path
 
    output_folder = "高等院校理工科教材化学史教程第三版电子书"  # Replace with your desired output folder
    pdf_path = "/Users/dako22/Downloads/高等院校理工科教材化学史教程第三版电子书.pdf"         # Replace with your PDF file path

    results = extract_figures_with_captions(pdf_path, output_folder)
    for r in results:
        print(f"Saved image on page {r['page']}: {r['image_path']}")
        print(f"Caption: {r['caption']}\n")
