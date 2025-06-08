from fastapi import APIRouter, FastAPI, UploadFile, File, HTTPException
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from PyPDF2 import PdfReader
import os
import tempfile

from pydantic import BaseModel
from app.config import settings
from app.logger import AppLogger

# Initialize embedding model
embedding_model = OpenAIEmbeddings()

# Initialize ChromaDB client (you can customize persist_directory)
chroma_db = Chroma(persist_directory=settings.chroma_db_path, embedding_function=embedding_model)

class PdfFile(BaseModel):
    File(...)

router = APIRouter()
logger = AppLogger.get_logger("crawler", level=settings.log_level, json_logs=True)

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    # else:
    #     logger.info(f"Received PDF file: {file.filename}")
    #return {"status": "success", "message": f"PDF {file.filename} processed and stored."}

    try:
        # Save uploaded PDF temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Extract text from PDF
        reader = PdfReader(tmp_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        os.remove(tmp_path)

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.create_documents([text])

        # Add documents to ChromaDB
        chroma_db.add_documents(docs)

        return {"status": "success", "message": f"PDF {file.filename} processed and stored."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
