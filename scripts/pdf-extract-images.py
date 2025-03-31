import fitz  # PyMuPDF
import os

def extract_figures_with_captions(pdf_path, output_folder, caption_threshold=50):
    """
    Extracts figures (images) and their associated captions from a PDF file.
    
    The function uses a heuristic to identify a caption by searching for text
    blocks immediately below each image block (within a vertical gap defined by
    caption_threshold) and with sufficient horizontal overlap.
    
    Args:
        pdf_path (str): Path to the PDF file.
        output_folder (str): Folder where the extracted images will be saved.
        caption_threshold (int): Maximum vertical gap (in points) between an image 
                                 and a text block to consider it as a caption.
    
    Returns:
        list of dict: Each dictionary contains:
            - 'page': The page number where the image was found.
            - 'image_path': The file path of the saved image.
            - 'caption': The extracted caption text (if found, otherwise an empty string).
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    doc = fitz.open(pdf_path)
    results = []
    
    # Process each page
    for page_num, page in enumerate(doc, start=1):
        # Get page content as a dictionary of blocks (text, images, etc.)
        page_dict = page.get_text("dict")
        image_blocks = []
        text_blocks = []
        
        # Separate image blocks and text blocks.
        for block in page_dict["blocks"]:
            if block["type"] == 1 and "xref" in block:
                image_blocks.append(block)
            elif block["type"] == 0:
                text_blocks.append(block)
        
        # Process each image block
        for i, img_block in enumerate(image_blocks, start=1):
            bbox = img_block["bbox"]  # Format: [x0, y0, x1, y1]
            xref = img_block["xref"]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_filename = os.path.join(output_folder, f"page{page_num}_fig{i}.{image_ext}")
            
            # Save the image to the output folder
            with open(image_filename, "wb") as img_file:
                img_file.write(image_bytes)
            
            # Heuristic: Find text blocks that appear just below the image block.
            caption_texts = []
            for txt_block in text_blocks:
                tbbox = txt_block["bbox"]
                # Check if the text block is below the image and within the threshold gap.
                if tbbox[1] >= bbox[3] and (tbbox[1] - bbox[3]) < caption_threshold:
                    # Ensure there is some horizontal overlap (at least 30% of the image width).
                    overlap = max(0, min(bbox[2], tbbox[2]) - max(bbox[0], tbbox[0]))
                    width_img = bbox[2] - bbox[0]
                    if width_img > 0 and (overlap / width_img) > 0.3:
                        caption_texts.append(txt_block["text"].strip())
            
            caption = " ".join(caption_texts)
            
            results.append({
                "page": page_num,
                "image_path": image_filename,
                "caption": caption
            })
    
    return results

# Example usage:
if __name__ == "__main__":
    #pdf_path = "sample.pdf"  # Replace with the path to your PDF file
    output_folder = "高等院校理工科教材化学史教程第三版电子书"  # Replace with your desired output folder
    pdf_path = "/Users/dako22/Downloads/高等院校理工科教材化学史教程第三版电子书.pdf"         # Replace with your PDF file path
    #output_folder = "extracted_images"  # Replace with your desired output folder

    figures = extract_figures_with_captions(pdf_path, output_folder)
    for fig in figures:
        print(f"Page {fig['page']}: Image saved at {fig['image_path']}")
        print(f"Caption: {fig['caption']}\n")
