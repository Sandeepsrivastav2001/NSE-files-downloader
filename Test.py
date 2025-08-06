import fitz  # PyMuPDF 1.24+
import os

# === File Paths ===
PDF_PATH = r"C:\Users\Administrator\Desktop\KYC-FORM9-13.pdf"
OUTPUT_PDF = r"C:\Users\Administrator\Desktop\KYC-FORM_Checkboxes.pdf"
DEBUG_FOLDER = r"C:\Users\Administrator\Desktop\Debug_Checkboxes"
os.makedirs(DEBUG_FOLDER, exist_ok=True)


# --- Step 1: Detect small vector checkboxes ---
def detect_vector_checkboxes(pdf_path, min_size=5, max_size=22):
    """
    Detect small square vector boxes (checkboxes) and ignore long rectangles.
    """
    doc = fitz.open(pdf_path)
    all_boxes = []

    for page_num, page in enumerate(doc):
        page_boxes = []

        for path in page.get_drawings():
            rect = path["rect"]
            if rect is None:
                continue

            w = rect.width
            h = rect.height
            aspect_ratio = w / h if h != 0 else 0
            area = w * h

            # Only small squares (checkbox-like)
            if (min_size <= w <= max_size and min_size <= h <= max_size
                and 0.75 <= aspect_ratio <= 1.25
                and 20 <= area <= 500):
                page_boxes.append(rect)

        all_boxes.append(page_boxes)
        print(f"Page {page_num+1}: Found {len(page_boxes)} vector checkboxes")

        # Save debug preview (optional)
        pix = page.get_pixmap(dpi=150)
        pix.save(os.path.join(DEBUG_FOLDER, f"page_{page_num+1}_debug.png"))

    doc.close()
    return all_boxes


# --- Step 2: Add interactive checkboxes with ✔ tick ---
def add_interactive_checkboxes(pdf_path, output_path, page_boxes):
    """
    Add clickable checkboxes that show a ✔ mark instead of * when clicked.
    """
    doc = fitz.open(pdf_path)

    for page_num, boxes in enumerate(page_boxes):
        page = doc[page_num]

        for idx, rect in enumerate(boxes):
            checkbox = fitz.Widget()
            checkbox.rect = rect
            checkbox.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
            checkbox.field_name = f"checkbox_{page_num}_{idx}"
            checkbox.field_flags = 0
            checkbox.field_value = "Off"  # Initially unticked
            checkbox.button_style = "check"  # ✅ Real checkmark style
            checkbox.text_color = (0, 0, 0)

            # Visual styling
            checkbox.border_width = 1
            checkbox.border_color = (0, 0, 0)
            checkbox.fill_color = (1, 1, 1)

            # Add to page
            page.add_widget(checkbox)

            # --- Generate ✔ appearance for all viewers ---
            with page.new_shape() as s:
                x0, y0, x1, y1 = rect
                size = min(x1 - x0, y1 - y0)
                # Draw a real ✔ mark
                s.move_to(x0 + size * 0.2, y0 + size * 0.5)
                s.line_to(x0 + size * 0.4, y0 + size * 0.2)
                s.line_to(x0 + size * 0.8, y0 + size * 0.8)
                s.finish(color=(0, 0, 0), width=1)
                checkbox.set_appearance(s)  # ✅ PyMuPDF 1.23+ method

        print(f"Page {page_num+1}: Added {len(boxes)} interactive checkboxes")

    doc.save(output_path, incremental=False, deflate=True)
    doc.close()


# --- Main Execution ---
if __name__ == "__main__":
    page_boxes = detect_vector_checkboxes(PDF_PATH, min_size=5, max_size=22)
    add_interactive_checkboxes(PDF_PATH, OUTPUT_PDF, page_boxes)

    print(f"\n✅ Updated PDF with ✔ checkboxes saved at:\n{OUTPUT_PDF}")
    print(f"Debug images saved in folder:\n{DEBUG_FOLDER}")
