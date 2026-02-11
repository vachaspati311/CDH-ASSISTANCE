import hashlib
from datetime import datetime

def generate_id(text):
    return hashlib.md5(text.encode()).hexdigest()[:12]

def timestamp():
    return datetime.now().isoformat()

def chunk_text(text, size=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start:start + size]
        chunks.append(chunk.strip())
        start += size - overlap
    return chunks
