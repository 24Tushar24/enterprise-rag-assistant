import fitz
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

def clean_text(text: str) -> str:
    # Multiple spaces ko single space mein convert karta hai
    text = re.sub(r"[ \t]+", " ", text)

    # Multiple blank lines ko single newline mein convert karta hai
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Starting/ending whitespace remove karta hai
    text = text.strip()

    return text


def extract_text_from_pdf(file_path: str) -> list[dict]:
    document = fitz.open(file_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        raw_text = page.get_text()
        cleaned_text = clean_text(raw_text)

        pages.append({
            "page": page_number,
            "text": cleaned_text
        })

    document.close()

    return pages

def chunk_pages(pages: list[dict]) -> list[dict]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = []

    for page in pages:

        page_chunks = splitter.split_text(page["text"])

        for chunk in page_chunks:
            chunks.append({
                "text": chunk,
                "page": page["page"]
            })

    return chunks