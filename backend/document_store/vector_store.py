import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import logging
from typing import List
import hashlib

logger = logging.getLogger(__name__)

# Configuration
DIMENSION = 384  # MiniLM dimension
CHUNK_SIZE = 300  # Words per chunk
OVERLAP = 50     # Words overlap between chunks
MAX_DOCUMENTS = 50  # Limit memory usage

# Initialize
model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.IndexFlatL2(DIMENSION)
documents = []  # Stores metadata
text_chunks = []  # Stores actual text chunks
chunk_metadata = []  # Stores which document each chunk came from

def get_chunk_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()

def split_into_chunks(text: str, filename: str) -> List[str]:
    """Smart chunking with paragraph awareness"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    # First split by paragraphs
    paragraphs = text.split('\n\n')
    
    for para in paragraphs:
        para_words = para.split()
        if len(para_words) <= CHUNK_SIZE:
            # Whole paragraph fits in one chunk
            chunks.append(para)
        else:
            # Need to split paragraph
            start = 0
            while start < len(para_words):
                end = start + CHUNK_SIZE
                chunk = ' '.join(para_words[start:end])
                chunks.append(chunk)
                start = end - OVERLAP  # Apply overlap
    
    logger.info(f"Split {filename} into {len(chunks)} chunks")
    return chunks

def add_document(text: str, filename: str) -> bool:
    try:
        if len(documents) >= MAX_DOCUMENTS:
            logger.warning(f"Document limit reached ({MAX_DOCUMENTS}), not adding {filename}")
            return False
            
        chunks = split_into_chunks(text, filename)
        if not chunks:
            logger.warning(f"No chunks generated for {filename}")
            return False
            
        # Generate embeddings in batches to save memory
        batch_size = 10
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            embeddings = model.encode(batch)
            
            # Add to index
            index.add(np.array(embeddings).astype('float32'))
            
            # Store metadata
            for chunk in batch:
                text_chunks.append(chunk)
                chunk_metadata.append({
                    "filename": filename,
                    "chunk_hash": get_chunk_hash(chunk)
                })
        
        documents.append({
            "filename": filename,
            "chunk_count": len(chunks),
            "total_chars": len(text)
        })
        
        logger.info(f"Added document {filename} with {len(chunks)} chunks")
        return True
        
    except Exception as e:
        logger.error(f"Error adding document {filename}: {str(e)}")
        return False

def search_documents(query: str, top_k: int = 3) -> str:
    try:
        if not text_chunks:  # No documents loaded
            return ""
            
        query_vec = model.encode([query])
        
        # Ensure we don't request more chunks than exist
        actual_top_k = min(top_k, len(text_chunks))
        
        distances, indices = index.search(
            np.array(query_vec).astype('float32'), 
            actual_top_k
        )
        
        results = []
        for i, idx in enumerate(indices[0]):
            if 0 <= idx < len(text_chunks):  # Validate index range
                results.append({
                    "text": text_chunks[idx],
                    "source": chunk_metadata[idx]["filename"],
                    "score": float(distances[0][i])
                })
        
        if not results:
            return ""
            
        # Sort by score (lower is better)
        results.sort(key=lambda x: x["score"])
        
        # Combine with source information
        context = "\n\n".join(
            f"From {r['source']} (relevance: {1-r['score']:.2f}):\n{r['text']}" 
            for r in results
        )
        
        logger.info(f"Found {len(results)} relevant chunks for query: {query}")
        return context
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return ""