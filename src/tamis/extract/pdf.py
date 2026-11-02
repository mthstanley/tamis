from tamis.extract import Extractor
import os
from urllib.parse import urlparse
from pypdf import PdfReader
from pypdf.errors import PdfReadError


class PDFExtractor(Extractor):
    def can_extract(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.scheme != "" and parsed.scheme != "file":
            return False
        if not os.path.exists(url):
            return False

        try:
            reader = PdfReader(url, strict=True)
            _ = reader.pdf_header
            if len(reader.pages) < 0:
                return False
            return True
        except (PdfReadError, Exception):
            return False

    def extract(self, url: str) -> str:
        reader = PdfReader(url, strict=True)
        full_text = ""
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                full_text += f"--- Page {page_num + 1} ---\n{text}\n"

        return full_text
