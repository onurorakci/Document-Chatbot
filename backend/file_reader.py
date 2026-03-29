import io
import fitz
from PIL import Image
import easyocr
import numpy as np

reader = easyocr.Reader(['en', 'tr'], gpu=False)


# File reading function that handles both PDFs and images, extracting text, tables, and performing OCR on images
async def file_read(file):
    global reader
    file_text = f"\n--- File: {file.filename} ---\n"

    if file.content_type == "application/pdf":
        content = await file.read()
        pdf = fitz.open(stream=content, filetype="pdf")

        for page_num, page in enumerate(pdf):
            # Text extraction
            text = page.get_text()
            if text.strip():
                file_text += text

            # 2. Tables extraction
            tables = page.find_tables()
            for table in tables:
                df = table.to_pandas()
                file_text += f"\n[TABLE {page_num + 1}]\n"
                file_text += df.to_string(index=False)
                file_text += "\n"

            # 3. Images and OCR
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                image_np = np.array(image)
                results = reader.readtext(image_np)
                if results:
                    ocr_text = " ".join([res[1] for res in results])
                    file_text += f"\n[IMAGE OCR - {page_num + 1}]\n{ocr_text}\n"

    elif file.content_type in ["image/jpeg", "image/png", "image/jpg"]:
        content = await file.read()
        image = Image.open(io.BytesIO(content)).convert("RGB")
        image_np = np.array(image)

        results = reader.readtext(image_np)
        file_text += " ".join([res[1] for res in results])

    return file_text