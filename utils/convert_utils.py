# utils/convert_utils.py

import os
import tempfile

from pdfminer.high_level import extract_text
from docx import Document
from PIL import Image
import pytesseract

def pdf_to_text(data: bytes) -> str:
    """
    Принимает байты PDF, сохраняет во временный файл и возвращает извлеченный текст.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        text = extract_text(tmp_path)
    finally:
        os.unlink(tmp_path)
    return text

def docx_to_text(data: bytes) -> str:
    """
    Принимает байты DOCX, сохраняет во временный файл и возвращает текст из параграфов.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        doc = Document(tmp_path)
        text = "\n".join(p.text for p in doc.paragraphs)
    finally:
        os.unlink(tmp_path)
    return text

def image_to_text(data: bytes, lang: str = "rus+eng") -> str:
    """
    Принимает байты изображения, сохраняет во временный файл и возвращает OCR-результат.
    Для русского текста lang='rus', для английского — 'eng', или комбинируйте.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        img = Image.open(tmp_path)
        text = pytesseract.image_to_string(img, lang=lang)
    finally:
        os.unlink(tmp_path)
    return text
