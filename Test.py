import fitz  # PyMuPDF
import cv2
import numpy as np

# ---------------------------
# File Paths
# ---------------------------
PDF_PATH = r"C:\Users\Administrator\Desktop\KYC-FORM9-13.pdf"
OUTPUT_PDF = r"C:\Users\Administrator\Desktop\My Work\Python.py\python with selenum\Output_Checkboxes.pdf"

# ---------------------------
# Step 1: Detect Checkboxes
# ---------------------------
def detect_checkboxes(pdf_path):
    doc = fitz.open(pdf_path)
    all_page_boxes = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)  # Render to image
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:  # Convert BGRA → BGR
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(blur, 180, 255, cv2.THRESH_BINARY_INV)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        page_boxes = []

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = w / float(h)
            area = w * h

            # Detect only small square-like boxes (filter out tables)
            if 10 < w < 50 and 10 < h < 50 and 0.8 < aspect_ratio < 1.2:
                rect = fitz.Rect(
                    x * page.rect.width / img.shape[1],
                    y * page.rect.height / img.shape[0],
                    (x + w) * page.rect.width / img.shape[1],
                    (y + h) * page.rect.height / img.shape[0]
                )
                page_boxes.append(rect)

        all_page_boxes.append(page_boxes)
        print(f"Page {page_num + 1}: Found {len(page_boxes)} vector checkboxes")

    return all_page_boxes

# ---------------------------
# Step 2: Add Interactive Checkboxes
# ---------------------------
def add_interactive_checkboxes(input_pdf, output_pdf, all_page_boxes):
    doc = fitz.open(input_pdf)

    for page_num, boxes in enumerate(all_page_boxes):
        page = doc[page_num]

        for i, rect in enumerate(boxes):
            # Optional: Draw a rectangle (debug)
            s = page.new_shape()
            s.draw_rect(rect)
            s.finish(width=0.5, color=(0, 0, 0))
            s.commit()

            # Add real PDF checkbox widget
            field_name = f"checkbox_p{page_num+1}_{i}"
            page.add_widget(
                rect,
                name=field_name,
                widget_type=fitz.PDF_WIDGET_TYPE_CHECKBOX,
                field_flags=0
            )

    doc.save(output_pdf)
    print(f"✅ Interactive checkboxes saved to {output_pdf}")

# ---------------------------
# Step 3: Run the Script
# ---------------------------
page_boxes = detect_checkboxes(PDF_PATH)
add_interactive_checkboxes(PDF_PATH, OUTPUT_PDF, page_boxes)
