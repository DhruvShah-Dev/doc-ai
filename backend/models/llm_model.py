from llama_cpp import Llama
import os
import logging
from typing import Optional
import time
import requests
import shutil

logger = logging.getLogger(__name__)

# Configuration - Phi-2 quantized model (small but capable)
MODEL_NAME = "phi-2.Q4_K_M.gguf"  # Quantized Phi-2 model (good balance of size/performance)
MODEL_URL = "https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf"  # Download link
MODEL_DIR = "models_folder"  # Local directory to store the model
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)

# Model configuration (optimized for Phi-2)
MODEL_CONFIG = {
    "n_ctx": 2048,        # Context window size
    "n_threads": 4,       # Optimal for 16GB RAM
    "n_batch": 128,       # Reduced batch size for stability
    "n_gpu_layers": 0,    # CPU-only
    "verbose": False
}

# Global model instance
llm = None

def download_model():
    """Download the model if it doesn't exist locally."""
    try:
        os.makedirs(MODEL_DIR, exist_ok=True)
        
        if os.path.exists(MODEL_PATH):
            logger.info("Model already exists. Skipping download.")
            return True
            
        logger.info(f"Downloading model from {MODEL_URL}...")
        start_time = time.time()
        
        with requests.get(MODEL_URL, stream=True) as r:
            with open(MODEL_PATH, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        
        download_time = time.time() - start_time
        logger.info(f"Model downloaded in {download_time:.2f} seconds")
        return True
        
    except Exception as e:
        logger.error(f"Model download failed: {str(e)}")
        return False

def initialize_model():
    global llm
    try:
        # Ensure model exists
        if not os.path.exists(MODEL_PATH):
            if not download_model():
                return False
                
        logger.info("Initializing LLM model...")
        start_time = time.time()
        
        llm = Llama(
            model_path=MODEL_PATH,
            **MODEL_CONFIG
        )
        
        load_time = time.time() - start_time
        logger.info(f"Model loaded in {load_time:.2f} seconds")
        return True
        
    except Exception as e:
        logger.error(f"Model initialization failed: {str(e)}")
        return False

def generate_answer(context: str, question: str) -> str:
    if not context:
        return "No relevant information found in documents."
        
    if not llm:
        if not initialize_model():
            return "System error: Model unavailable"
    
    try:
        # Optimized prompt for Phi-2
        prompt = f"""### Task:
Answer the question using ONLY the provided context extracts from documents.
If the answer isn't found, say you don't know.

### Context Extracts:
{context[:1800]}  # Slightly larger context window

### Question:
{question}

### Guidelines:
1. Be concise but thorough
2. Cite which document the information came from
3. If unsure, say "I don't know"

### Answer:"""
        
        # Generation parameters for Phi-2
        output = llm(
            prompt=prompt,
            max_tokens=350,
            temperature=0.3,
            top_p=0.9,
            repeat_penalty=1.1,
            stop=["\n###", "Document:"]
        )
        
        answer = output['choices'][0]['text'].strip()
        
        # Post-processing
        if not answer:
            return "I couldn't determine an answer from the documents."
            
        if question.lower() in answer.lower():
            return "The documents mention this topic but don't provide a clear definition."
            
        return answer
        
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        return "Error generating response"