# DocAI: local document question answering

DocAI is a prototype for asking questions about text in PDF, DOCX, and TXT files. A FastAPI backend extracts text, indexes it with Sentence Transformers and FAISS, and passes retrieved context to a local Phi-2 model through `llama-cpp-python`. A browser interface supports uploads and chat.

Document processing and answer generation run on your computer. The model is downloaded from Hugging Face on first use, and the browser interface loads React, Babel, Tailwind, and icons from public CDNs. An internet connection is therefore needed for initial setup and the current browser UI.

## What is in this repository

- `backend/main.py`: upload, question, and health endpoints
- `backend/document_store/`: text extraction and FAISS indexing
- `backend/models/llm_model.py`: Phi-2 model download and inference
- `frontend/`: static React interface loaded through CDN scripts

## Run locally

Install Python dependencies from the repository root:

```bash
python -m venv .venv
python -m pip install -r backend/requirements.txt
```

Start the API from `backend/` so its relative model and upload paths resolve there:

```bash
cd backend
python -m uvicorn main:app --reload
```

In another terminal, serve the static frontend from the repository root:

```bash
python -m http.server 5173 --directory frontend
```

Open [http://localhost:5173](http://localhost:5173), upload a text-based PDF, DOCX, or TXT file, and ask a question. The frontend calls the API at `http://localhost:8000`. The API health endpoint is [http://localhost:8000/health](http://localhost:8000/health).

The first question triggers a download of the quantized Phi-2 GGUF model into `backend/models_folder/`, unless it is already present. This can take time and needs free disk space. Uploaded files go into `backend/uploaded_files/`. Both directories are excluded from Git.

## How it works

1. The upload endpoint checks the file extension and a 10 MB size limit.
2. The backend extracts text and adds it to a FAISS index.
3. A question retrieves matching text and sends it to the local model to generate an answer.

## Limits and privacy notes

- Scanned PDFs need OCR, which this project does not provide.
- Generated answers can be incorrect; check them against the source documents.
- The frontend uses CDN scripts, and the model downloads from Hugging Face. For an offline deployment, vendor those assets and provide the model locally.
- This is a local research prototype. Its API uses permissive CORS and has no authentication; do not expose it to untrusted networks.
- The repository does not include a license file.