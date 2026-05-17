import argparse
import json
import os
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


TEXT_EXTS = {".txt", ".md", ".markdown", ".csv", ".log", ".yaml", ".yml"}
JSON_EXTS = {".json"}
DOCX_EXTS = {".docx"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff"}


def _read_text_with_fallback(path: Path) -> str:
    encodings = ["utf-8", "utf-8-sig", "gbk", "gb18030", "latin-1"]
    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"cannot decode text file: {path}")


def _read_json(path: Path) -> str:
    text = _read_text_with_fallback(path)
    data = json.loads(text)
    return json.dumps(data, ensure_ascii=False, indent=2)


def _read_docx(path: Path) -> str:
    with zipfile.ZipFile(path, "r") as zf:
        with zf.open("word/document.xml") as fp:
            xml_bytes = fp.read()

    root = ET.fromstring(xml_bytes)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []
    for paragraph in root.findall(".//w:p", ns):
        texts = []
        for node in paragraph.findall(".//w:t", ns):
            texts.append(node.text or "")
        line = "".join(texts).strip()
        if line:
            paragraphs.append(line)
    return "\n".join(paragraphs)


def _ocr_with_pytesseract(path: Path):
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        return None

    image = Image.open(path)
    text = pytesseract.image_to_string(image, lang="chi_sim+eng")
    return text.strip()


def _ocr_with_rapidocr(path: Path):
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        return None

    engine = RapidOCR()
    result, _ = engine(str(path))
    if not result:
        return ""
    return "\n".join(item[1] for item in result if len(item) > 1 and item[1])


def _read_image(path: Path) -> str:
    text = _ocr_with_pytesseract(path)
    if text is not None:
        return text

    text = _ocr_with_rapidocr(path)
    if text is not None:
        return text

    raise RuntimeError(
        "image OCR backend not available. Install one of: "
        "'pytesseract' (+ pillow + tesseract binary) or 'rapidocr_onnxruntime'."
    )


def extract_one(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in TEXT_EXTS:
        return _read_text_with_fallback(path).strip()
    if ext in JSON_EXTS:
        return _read_json(path).strip()
    if ext in DOCX_EXTS:
        return _read_docx(path).strip()
    if ext in IMAGE_EXTS:
        return _read_image(path).strip()
    raise ValueError(f"unsupported file type: {path.suffix} ({path})")


def main():
    parser = argparse.ArgumentParser(
        description="Extract normalized requirement text from docs/images for test-case generation."
    )
    parser.add_argument("--input", nargs="+", required=True, help="Input file path(s).")
    parser.add_argument("--output", required=True, help="Output merged text file.")
    args = parser.parse_args()

    parts = []
    for raw_path in args.input:
        path = Path(raw_path)
        if not path.exists():
            raise FileNotFoundError(f"input not found: {path}")
        content = extract_one(path)
        section = f"# Source: {path}\n{content}\n"
        parts.append(section)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged = "\n".join(parts).strip() + "\n"
    output_path.write_text(merged, encoding="utf-8")

    print(f"OK: extracted {len(parts)} file(s) -> {output_path.resolve()}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
