import base64
import shutil
import tempfile
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from core.srv.text_process.docling_preprocessor import docling_debug_export
from core.srv.text_process.text_processor import TextProcessor
from core.srv.vectorstore.chroma_db import Chroma_db
from core.type.base.base_result import BaseResult
from endpoint.models.file_model import DeleteFileModel , FileProcessingRequest, FileProcessingResult

router = APIRouter(prefix="/datasource", tags=["Datasource Endpoints"])

@router.post("/process-file/", response_model=BaseResult[FileProcessingResult])
async def process_file(
    assistant_id: str = Form(...),  
    doc_id: str = Form(...),       
    file: UploadFile = File(...),
    file_name:str = Form(...),
    file_size:str = Form(...),
    file_type:str = Form(...)):
    try:
        # Check if the uploaded file is a PDF
        if file.content_type != "application/pdf":
            return BaseResult.error_response(message="File must be a PDF" , error_code=400)
        # Read the file content as bytes
        file_bytes = await file.read()
        # Extract text from the PDF using PyMuPDF
        content = TextProcessor.extract_text_from_pdf(file_bytes)

        chroma_client = Chroma_db() 

        chunks = TextProcessor.split_text(content,500,50)
        docs , ids = chroma_client.chunks_to_docs(chunks , f"{doc_id}_")
        metadatas = [{"type": "text" , "doc_id":doc_id} for id in ids]
        chroma_client.add_documents(assistant_id ,metadatas, docs , ids)
        result = FileProcessingResult(
            assistant_id=assistant_id,
            doc_id=doc_id,
            processed_data=content,
            is_processed=True,
            file_size=0
        )
        return BaseResult.success_response(data= result)
    except Exception  as e:
        return BaseResult.error_response(message= str(e), error_code=500)
    except HTTPException  as e:
        return BaseResult.error_response(message= e.detail , error_code=int(e.status_code))

@router.post("/delete-file/", response_model=BaseResult[str])
async def delete_file(model:DeleteFileModel):
    try:
        chroma_client = Chroma_db() 
        chroma_client.delete_file(assistant_id=model.assistant_id.lower(), doc_id=model.doc_id.lower())
        return BaseResult.success_response(data= f"file {model.doc_id} from collection {model.assistant_id} successfully deleted")
    except Exception  as e:
        return BaseResult.error_response(message= str(e), error_code=503)
    except HTTPException  as e:
        return BaseResult.error_response(message= e.detail , error_code=int(e.status_code))
@router.post("/process-file-base64/", response_model= BaseResult[FileProcessingResult] )
async def process_file_base64(request: FileProcessingRequest):
    PDF_MIME = "application/pdf"
    DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    content = []
    raw_result = []
    ids = []
    docs = []
    metadatas = []
    chroma_client = Chroma_db()
    try:
        try:
            file_bytes = base64.b64decode(request.file_base64)
            
        except Exception as e:
            print(e)
            return BaseResult.error_response(message="Invalid base64 encoding" , error_code=400)
        if  request.file_type == PDF_MIME:
            pdf_content = TextProcessor.extract_text_from_pdf(file_bytes)
            chunks = TextProcessor.split_text(pdf_content, 500, 50)
            docs, ids = chroma_client.chunks_to_docs(chunks, f"{request.doc_id}_")
            metadatas = [{
                        "doc_id": request.doc_id,
                        "head": "Unknown",
                        "chunk_index": chunk_index,
                        "token_count": 0,
                        "assistant_id": request.assistant_id,
                        "source": "pdf",
                        "language": "fa",
                        "version": "v1",

            } for  chunk_index, id in enumerate(ids)]
        elif request.file_type == DOCX_MIME:
            with tempfile.NamedTemporaryFile(delete=False, suffix="test") as tmp_file:
                content = file_bytes
                tmp_file.write(content)
                tmp_path = tmp_file.name
                raw_result = docling_debug_export(source=tmp_path, source_type=request.file_name, doc_id=request.doc_id, assistant_id=request.assistant_id)
                for c in raw_result:   
                    ids.append(c['id'])
                    docs.append(c['content'])
                    metadatas.append(c['metadata'])  
                #ids = [c["id"] for c in raw_result]
                #docs = [c["content"] for c in raw_result]
                #metadatas = [c["metadata"] for c in raw_result]
        else:
            return BaseResult.error_response(message="Unsupported file type" , error_code=400)
        print(f"Adding {len(docs)} documents to collection '{request.assistant_id}' with doc_id prefix '{request.doc_id}_'")
        chroma_client.add_documents(request.assistant_id,docs, metadatas, ids)
        response_model = FileProcessingResult(
            assistant_id=request.assistant_id,
            doc_id=request.doc_id,
            is_processed=True,
            message="file processed successfully"
        )
        return BaseResult.success_response(data=response_model)

    except Exception  as e:
        print(e)
        return BaseResult.error_response(message= str(e), error_code=500)
    except HTTPException  as e:
        print(e)
        return BaseResult.error_response(message= e.detail , error_code=int(e.status_code))

@router.post("/docling-process-file/")  
async def  docling_process_file(request: FileProcessingRequest):
    content = ""
    try:
        file_bytes = base64.b64decode(request.file_base64)
        
    except Exception as e:
        print(e)
        return BaseResult.error_response(message="Invalid base64 encoding" , error_code=400)
    with tempfile.NamedTemporaryFile(delete=False, suffix="test") as tmp_file:
        content = file_bytes
        tmp_file.write(content)
        tmp_path = tmp_file.name
        raw_result = docling_debug_export(tmp_path)
        #raw_result = prepare_structured_chunks(tmp_path)
        return raw_result

@router.post("/docling-process-file-new/")
async def docling_process_file_new(
    file: UploadFile = File(...)
):
    try:
        # ساخت فایل موقت با همان پسوند
        suffix = "." + file.filename.split(".")[-1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name

        # پردازش با docling
        raw_result = docling_debug_export(tmp_path , suffix , file.filename , "assistant_id" , "persian_embedding")
        # یا
        # raw_result = prepare_structured_chunks(tmp_path)

        return raw_result

    except Exception as e:
        print(e)
        return BaseResult.error_response(
            message="File processing failed",
            error_code=500
        )

