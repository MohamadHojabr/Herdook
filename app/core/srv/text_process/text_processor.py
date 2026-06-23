import re
from typing import List
import pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter

class   TextProcessor :
    def clean_persian_text(text):
        # Normalize Arabic to Persian characters
        replacements = {
            'ك': 'ک',
            'ي': 'ی',
            'ۀ': 'ه',
            'ة': 'ت',
            '\u0643': 'ک',  # Arabic kaf
            '\u0649': 'ی',  # Arabic alef maksura
            '\u0629': 'ه',  # Arabic teh marbuta
        }
        
        for ar, fa in replacements.items():
            text = text.replace(ar, fa)
            # Clean whitespace and control characters
        text = re.sub(r'\s+', ' ', text)  # Multiple whitespace to single space
        text = re.sub(r'\n+', '\n', text)  # Multiple newlines to single
        text = re.sub(r'[ـ\r]', '', text)  # Remove tatweel and carriage returns
    
        # Normalize Persian punctuation spacing
        punctuation = {'،', '؛', '؟', '!'}
        for mark in punctuation:
            text = re.sub(fr'\s*{mark}\s*', f'{mark} ', text)
    
        # Remove leading/trailing whitespace
        text = text.strip()
    
        return text
    @classmethod
    def split_text(self ,text , CHUNK_SIZE , CHUNK_OVERLAP):
            # Split on page boundaries first
        pages = re.split(r'\nPAGE_SEPARATOR_\d+\n', text)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=[
            "\n\n", 
            ".\n", 
            "۔",  # Urdu/Persian full stop
            "؟",   # Question mark
            "!\n", 
            "\n", 
            " ",   # Regular space
            "‌",   # Zero-width non-joiner
            ],
            keep_separator=True
        )
        all_chunks = []
        for page in pages:
            if page.strip():
               chunks = splitter.split_text(page)
               all_chunks.extend(chunks)
        return all_chunks
    @classmethod
    def extract_text_from_pdf(self ,file_bytes: bytes) -> str:
        text = ""
        try:
            pdf_document = pymupdf.open(stream=file_bytes, filetype="pdf")
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
            text = self.clean_persian_text(text)

            cleaned_data = re.sub(r"\.+", "", text)

            cleaned_data = " ".join(cleaned_data.split())
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {e}")
        return cleaned_data

# Helper function to extract paragraphs from PDF using PyMuPDF
def extract_paragraphs_from_pdf(file_bytes: bytes) -> List[str]:
    paragraphs = []
    try:
        # Open the PDF from bytes
        pdf_document = pymupdf.open(stream=file_bytes, filetype="pdf")
        # Iterate through pages
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            # Extract text blocks
            blocks = page.get_text("blocks")
            for block in blocks:
                # Each block contains: (x0, y0, x1, y1, text, block_no, block_type)
                text = block[4].strip()  # Extract text and remove leading/trailing spaces
                if text:  # Only add non-empty text
                    paragraphs.append(text)
    except Exception as e:
        raise ValueError(f"Error extracting paragraphs from PDF: {e}")
    return paragraphs

