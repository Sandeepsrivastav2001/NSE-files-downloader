import fitz  # PyMuPDF
import cv2
import numpy as np

INPUT_PDF = r"C:\Users\Administrator\Desktop\KYC-FORM9-13.pdf"
OUTPUT_PDF = r"C:\Users\Administrator\Desktop\output_checkboxes.pdf"

print("Using PyMuPDF version:", fitz.version[0])

def detect_checkboxes(pdf_path):
    doc = fitz.open(pdf_path)
    page_boxes = []
    for page_num, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        boxes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = w / float(h)
            if 12 <= w <= 35 and 12 <= h <= 35 and 0.75 <= aspect_ratio <= 1.25:
                rect = [
                    x * page.rect.width / img.shape[1],
                    page.rect.height - (y + h) * page.rect.height / img.shape[0],
                    (x + w) * page.rect.width / img.shape[1],
                    page.rect.height - y * page.rect.height / img.shape[0]
                ]
                boxes.append(rect)
        print(f"Page {page_num+1}: Found {len(boxes)} checkboxes")
        page_boxes.append(boxes)
    return page_boxes


def add_interactive_checkboxes(input_pdf, output_pdf, page_boxes):
    doc = fitz.open(input_pdf)
    for page_num, boxes in enumerate(page_boxes):
        page = doc[page_num]
        for idx, rect in enumerate(boxes):
            checkbox_rect = fitz.Rect(rect)
            page.add_checkbox_widget(
                checkbox_rect,
                field_name=f"Check_{page_num+1}_{idx+1}",
                value=False
            )
    doc.save(output_pdf)
    print(f"✅ Interactive PDF saved: {output_pdf}")


if __name__ == "__main__":
    page_boxes = detect_checkboxes(INPUT_PDF)
    add_interactive_checkboxes(INPUT_PDF, OUTPUT_PDF, page_boxes)
