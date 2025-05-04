Here’s your refined **README.md** with improved structure, clarity, and technical depth:

---

# **📄 Document-Based AI Assistant**  
**A local, privacy-first AI chatbot that answers questions using your documents—no cloud APIs, no data leaks.**  

Powered by **Phi-2** (optimized for CPU) and **FAISS** for semantic search, this tool extracts insights from PDFs, DOCX, and TXT files while keeping all data on your machine.  

---

## **✨ Key Features**  
| Feature | Description |  
|---------|-------------|  
| **📂 Document Support** | PDF, DOCX, TXT (text-based only) |  
| **🔍 Semantic Search** | FAISS + `all-MiniLM-L6-v2` embeddings for relevancy ranking |  
| **🤖 Local LLM** | Quantized Phi-2 (4-bit GGUF) via `llama.cpp` |  
| **🚫 No GPU Needed** | Runs efficiently on CPU (16GB RAM recommended) |  
| **🌐 Responsive UI** | React frontend with drag-and-drop uploads |  

---

## **⚙️ Tech Stack**  
### **Backend (Python)**  
- **Framework**: FastAPI  
- **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`)  
- **Vector DB**: FAISS (local)  
- **Text Extraction**: `pdfplumber`, `python-docx`  
- **LLM**: Phi-2 (4-bit quantized via `llama.cpp`)  

### **Frontend (JavaScript)**  
- **UI**: React + Tailwind CSS  
- **Build**: Vite (optional)  

---

## **🚀 Installation**  
### **1. Clone & Setup**  
```bash  
git clone https://github.com/DhruvShah-Dev/doc-ai.git  
cd doc-ai  
```  

### **2. Backend Setup**  
```bash  
pip install -r backend/requirements.txt  
```  
**Download Phi-2 Model**:  
```bash  
wget https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf -O backend/models/phi-2.Q4_K_M.gguf  
```  

### **3. Run the System**  
**Backend (FastAPI)**:  
```bash  
cd backend && uvicorn main:app --reload  
```  
**Frontend (React)**:  
```bash  
cd frontend && npm install && npm run dev  
```  

---

## **📂 Project Structure**  
```  
doc-ai/  
├── backend/                  # FastAPI server  
│   ├── models/               # Model to generate answers
        ├──__init__.py
        └──llm_model.py
│   ├── document_store/       # Text processing & FAISS
        ├──__init__.py
        ├──text_extractor.py
        └──vector_store.py
    ├──models_folder/          # Phi-2 GGUF model will be downloaded here
    ├──uploaded_files/         # All the uploaded files will be present here
    ├──requirements.txt        # Download these before starting
│   └── main.py               # API endpoints  
├── frontend/                 # React app  
│   ├── public/               # Static assets  
│   └── src/                  # UI components  
└── .gitignore                # Excludes models_folder/  
```  

---

## **🔧 Configuration**  
### **Backend (`backend/main.py`)**  
| Setting | Purpose | Default |  
|---------|---------|---------|  
| `UPLOAD_FOLDER` | Document storage path | `uploaded_files/` |  
| `MAX_FILE_SIZE_MB` | File size limit | `10` |  

### **LLM (`backend/models/llm_model.py`)**  
| Parameter | Effect | Recommended |  
|-----------|--------|-------------|  
| `n_ctx` | Context window | `2048` |  
| `temperature` | Answer creativity | `0.3` (factual) |  

---

## **🛠️ How It Works**  
1. **Upload** → Documents are split into chunks and vectorized.  
2. **Query** → FAISS retrieves top-3 relevant passages.  
3. **Answer** → Phi-2 generates responses from context.  

**Example Queries**:  
- *“Summarize the key points.”*  
- *“What’s the conclusion of this paper?”*  

---

## **⚠️ Limitations**  
- **No OCR**: Scanned PDFs unsupported.  
- **Hardware**: Requires ≥8GB RAM for smooth operation.  

---

## **📜 License**  
MIT License.  
**Contact**: [@DhruvShah-Dev](https://github.com/DhruvShah-Dev)  

---

**Deploy locally and own your data!** 🔒🚀  
