import pdfplumber
import docx
import logging
from typing import Optional
import io

logger = logging.getLogger(__name__)

def extract_text(filepath: str) -> Optional[str]:
    try:
        logger.info(f"Extracting text from {filepath}")
        
        if filepath.endswith('.pdf'):
            text = ""
            with pdfplumber.open(filepath) as pdf:
                for i, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"Page {i+1}:\n{page_text}\n\n"
                    except Exception as e:
                        logger.warning(f"Error on page {i+1}: {str(e)}")
                        continue
            return text.strip()
            
        elif filepath.endswith('.docx'):
            doc = docx.Document(filepath)
            return "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            
        elif filepath.endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
                
        else:
            raise ValueError("Unsupported file format")
            
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        raise