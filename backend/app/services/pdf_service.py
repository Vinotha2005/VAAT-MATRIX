import fitz  # PyMuPDF
import pdfplumber
from typing import Dict, List
from pathlib import Path
import pytesseract
from PIL import Image


def extract_text(filepath: str) -> Dict:
    """
    Extracts basic structure (pages, headings heuristic, paragraphs) from a PDF.
    Uses PyMuPDF and falls back to pdfplumber and OCR for scanned pages.
    Returns a dict with `pages` list and `text` full text.
    """
    doc = fitz.open(filepath)
    pages = []
    full_text = []
    for i in range(len(doc)):
        page = doc.load_page(i)
        text = page.get_text("text")
        if not text.strip():
            # try OCR via pdfplumber images -> pytesseract
            try:
                with pdfplumber.open(filepath) as pdf:
                    p = pdf.pages[i]
                    pil = p.to_image(resolution=150).original
                    ocr = pytesseract.image_to_string(pil)
                    text = ocr
            except Exception:
                text = ""
        pages.append({"page_number": i+1, "text": text})
        full_text.append(text)
    return {"pages": pages, "text": "\n\n".join(full_text)}
