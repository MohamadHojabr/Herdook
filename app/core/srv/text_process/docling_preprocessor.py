import datetime
import os
# مسیر مدل‌ها (اگر می‌خوای بعداً مدل محلی استفاده کنی)
#MODELS_DIR = r"D:\Work\Ai_Assistant\ai-core\app\local_models\docling\models"

# کاملاً آفلاین و بدون مدل سنگین
#os.environ["TRANSFORMERS_OFFLINE"] = "0"
#os.environ["HF_HUB_OFFLINE"] = "0"
# این خط مهم نیست اگر مدل سنگین استفاده نمی‌کنیم
#os.environ["DOCLING_SERVE_ARTIFACTS_PATH"] = MODELS_DIR

import re
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from langchain_text_splitters import RecursiveCharacterTextSplitter

def docling_debug_export(source: str, source_type: str, doc_id: str, assistant_id: str):
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = False

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    
    result = converter.convert(source)
    doc = result.document.export_to_text()

    section_splitter = RecursiveCharacterTextSplitter(
        separators=["##", "###"],
        keep_separator=True
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        keep_separator=True
    )

    section_chunks = section_splitter.split_text(doc)

    final_chunks = []

    for section_index, section in enumerate(section_chunks):
        raw_head = extract_section(section)
        head = extract_head_smart(section, raw_head)

        chunks = splitter.split_text(section)

        buffer_text = ""
        buffer_tokens = 0
        buffer_chars = 0
        chunk_index = 0

        for chunk in chunks:
            chunk_tokens = estimate_tokens(chunk)
            chunk_chars = len(chunk)

            # اگر اضافه کردن این chunk هنوز تو limit هست
            if buffer_tokens + chunk_tokens <= 500:
                buffer_text += ("\n\n" + chunk if buffer_text else chunk)
                buffer_tokens += chunk_tokens
                buffer_chars += chunk_chars
            else:
                # buffer فعلی رو ثبت کن
                final_chunks.append({
                    "id": f"{doc_id}_{section_index}_{chunk_index}",
                    "content": buffer_text,
                    "embedding": None, 
                    "metadata": {
                        "doc_id": doc_id,
                        "head": head,
                        "chunk_index": chunk_index,
                        "token_count": buffer_tokens,
                        "assistant_id": assistant_id,
                        "source": source_type,
                        "language": "fa",
                        "version": "v1",
                    }
                })

                chunk_index += 1

                # buffer جدید
                buffer_text = chunk
                buffer_tokens = chunk_tokens
                buffer_chars = chunk_chars

        # باقی‌مانده buffer
        if buffer_text.strip():
            final_chunks.append({
                "id": f"{doc_id}_{section_index}_{chunk_index}",
                "content": buffer_text,
                "embedding": None,
                "metadata": {
                    "doc_id": doc_id,
                    "head": head,
                    "chunk_index": chunk_index,
                    "token_count": buffer_tokens,
                    "assistant_id": assistant_id,
                    "source": source_type,
                    "language": "fa",
                    "version": "v1",
                }
            })

    return final_chunks

def estimate_tokens(text: str) -> int:
    return int(len(text.split()) * 1.3)
def extract_head_smart(chunk: str, extracted_head: str | None = None) -> str:
    # 1️⃣ اگر head معتبر داریم
    if extracted_head and extracted_head.strip():
        return extracted_head.strip()

    text = chunk.strip()

    # 2️⃣ تلاش برای bold title
    bold_pattern = r"^\*\*(.+?)\*\*"
    bold_match = re.search(bold_pattern, text)
    if bold_match:
        title = bold_match.group(1).strip()
        if 3 <= len(title.split()) <= 12:
            return title

    # 3️⃣ جمله اول به عنوان عنوان
    sentence_match = re.split(r"[.\n؟!]", text, maxsplit=1)
    if sentence_match:
        sentence = sentence_match[0].strip()

        # پاکسازی عنوان
        sentence = re.sub(r"^[^آ-یa-zA-Z0-9]+", "", sentence)
        sentence = re.sub(r"\s+", " ", sentence)

        words = sentence.split()
        if 3 <= len(words) <= 14:
            return sentence

        # کوتاه‌سازی در صورت طولانی بودن
        return " ".join(words[:12])

    # 4️⃣ fallback نهایی
    return "بدون عنوان"
def extract_section(text):
    lines = text.split('\n')
    result = []
    in_section = False
    
    for line in lines:
        if line.startswith('##'):
            in_section = True
            clean_line = line.lstrip('#').strip()
            result.append(clean_line)
        elif in_section:
            if line.strip() == '':  # اگر به خط خالی رسیدیم
                break
            result.append(line)
    
    return '\n'.join(result)


    
