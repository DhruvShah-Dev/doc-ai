from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from document_store.text_extractor import extract_text
from document_store.vector_store import add_document, search_documents
from models.llm_model import generate_answer
import os
import asyncio
import time
from typing import Optional
import logging
import pdfplumber

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
MAX_FILE_SIZE_MB = 10  # 10MB maximum file size
SUPPORTED_FILE_TYPES = [".pdf", ".docx", ".txt"]

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Validate file
        file_size = 0
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to start
        
        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File too large. Max size is {MAX_FILE_SIZE_MB}MB")
        
        if not any(file.filename.lower().endswith(ext) for ext in SUPPORTED_FILE_TYPES):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Save file
        file_location = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_location, "wb+") as f:
            f.write(await file.read())
        
        logger.info(f"Processing file: {file.filename}")
        
        # Extract and index text
        start_time = time.time()
        text = extract_text(file_location)
        logger.info(f"Extracted text length: {len(text)} chars")
        
        success = add_document(text, file.filename)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to index document")
        
        process_time = time.time() - start_time
        logger.info(f"Processed in {process_time:.2f} seconds")
        
        return JSONResponse(
            content={
                "status": "success",
                "filename": file.filename,
                "processing_time": f"{process_time:.2f}s"
            }
        )
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask/")
async def ask_question(question: str = Form(...)):
    try:
        logger.info(f"Question received: {question}")
        start_time = time.time()
        
        # Get relevant context with timing
        context_start = time.time()
        context = search_documents(question)
        context_time = time.time() - context_start
        logger.info(f"Context search took {context_time:.2f}s")
        
        # Generate answer with timeout
        answer_start = time.time()
        try:
            answer = await asyncio.wait_for(
                asyncio.to_thread(generate_answer, context, question),
                timeout=60  # 1 minute timeout
            )
        except asyncio.TimeoutError:
            logger.warning("Answer generation timed out")
            raise HTTPException(status_code=504, detail="Processing timeout")
        
        answer_time = time.time() - answer_start
        total_time = time.time() - start_time
        
        logger.info(f"Answer generated in {answer_time:.2f}s (Total: {total_time:.2f}s)")
        logger.debug(f"Answer: {answer}")
        
        return JSONResponse(
            content={
                "status": "success",
                "answer": answer,
                "timings": {
                    "context_search": f"{context_time:.2f}s",
                    "answer_generation": f"{answer_time:.2f}s",
                    "total": f"{total_time:.2f}s"
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Question error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}