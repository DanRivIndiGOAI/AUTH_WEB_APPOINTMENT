import re
import fitz  # PyMuPDF
import easyocr
import numpy as np

reader = easyocr.Reader(['es', 'en'])

pdf_path = 'Autorizaciones.pdf'
doc = fitz.open(pdf_path)

for i, page in enumerate(doc, start=1):
    pix = page.get_pixmap(dpi=200)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)

    pix.save(f'EPS_{i}.jpg')

    result = reader.readtext(img, detail=0, paragraph=True)
    full_text = "\n".join(result)

    print(f'--- Página {i} ---')

    if i == 1:
        auth_match = re.search(r"N['\u2019°?]\s*Autoriz[aá]ci[oó]n[:\s]+(.+?)(?:\s*C[oó]d)", full_text)
        cups_match = re.search(r'\[(\d+)\]', full_text)

        num_autorizacion = auth_match.group(1).strip() if auth_match else "No encontrado"
        cups = cups_match.group(1) if cups_match else "No encontrado"

        print(f"N° Autorización: {num_autorizacion}")
        print(f"CUPS: {cups}")
    else:
        print(full_text)

    print()

doc.close()
