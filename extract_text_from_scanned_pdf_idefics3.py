import os
import json
import base64
from io import BytesIO
from pdf2image import convert_from_path
from PIL import Image
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

# Load the InferenceClient for Idefics3
client = InferenceClient("HuggingFaceM4/Idefics3-8B-Llama3")


def encode_image(image: Image.Image) -> str:
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


def ask_image_question(image: Image.Image, question: str = "Please describe the contents of this page.") -> str:
    image_data = encode_image(image)
    image_tag = f"![image]({image_data})"

    prompt = f"{image_tag}\n\n{question}"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
        },
    }

    response = client.post(json=payload)
    try:
        return json.loads(response.decode())[0]
    except Exception as e:
        print("⚠️ Error parsing response:", e)
        return "[Error extracting text]"


def extract_text_from_pdf(pdf_path: str, output_dir: str = "output"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pages = convert_from_path(pdf_path)
    results = []

    for i, page in enumerate(pages):
        print(f"📝 Processing page {i + 1}/{len(pages)}...")
        text = ask_image_question(page)
        image_path = os.path.join(output_dir, f"page_{i+1}.jpg")
        page.save(image_path, "JPEG")
        results.append({
            "page": i + 1,
            "image": image_path,
            "description": text
        })

    json_path = os.path.join(output_dir, "extracted_text.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Done. Extracted text saved to: {json_path}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python extract_text_from_scanned_pdf_idefics3.py <path_to_pdf>")
    else:
        extract_text_from_pdf(sys.argv[1])
