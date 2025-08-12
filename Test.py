import fitz  # PyMuPDF

input_pdf = r"C:\Users\Administrator\Desktop\KYC-FORM9-13.pdf"
output_pdf = r"C:\Users\Administrator\Desktop\KYC-FORM9-interactive.pdf"

doc = fitz.open(input_pdf)

# Example positions — replace with detection results
checkboxes = [
    (100, 150, 115, 165),
    (100, 180, 115, 195)
]

for page_index, page in enumerate(doc):
    if page_index == 0:
        for i, rect in enumerate(checkboxes):
            widget = page.new_widget(
                rect=fitz.Rect(rect),
                field_name=f"chk_{page_index}_{i}",
                field_type=fitz.PDF_WIDGET_TYPE_CHECKBOX
            )
            widget.field_value = "Off"   # Start unchecked
            widget.update()

doc.save(output_pdf)
doc.close()

print(f"✅ PDF saved with interactive checkboxes: {output_pdf}")
