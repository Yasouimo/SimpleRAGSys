# file: indexer.py
import faiss, numpy as np, os, json
from sentence_transformers import SentenceTransformer
from rag_utils import normalize_text, chunk_text, extract_text_from_pdf, extract_text_from_md

EMB_MODEL_NAME = "all-MiniLM-L6-v2"
MODEL = SentenceTransformer(EMB_MODEL_NAME)

def embed_texts(texts, batch_size=16):  # Reduced batch size
    """Embed texts in smaller batches to save memory"""
    if not texts:
        return np.array([]).reshape(0, 384)
    
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = MODEL.encode(batch, convert_to_numpy=True, show_progress_bar=False)
        all_embeddings.append(embeddings)
    
    return np.vstack(all_embeddings) if all_embeddings else np.array([]).reshape(0, 384)

class FaissIndex:
    def __init__(self, dim=384):
        self.dim=dim
        self.index = faiss.IndexFlatIP(dim)
        self.metadata = []

    def add(self, vectors: np.ndarray, metas: list):
        if vectors.shape[0] == 0:
            return
        faiss.normalize_L2(vectors)
        self.index.add(vectors)
        self.metadata.extend(metas)

    def save(self, path_index="index.faiss", path_meta="meta.json"):
        faiss.write_index(self.index, path_index)
        with open(path_meta, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def load(self, path_index="index.faiss", path_meta="meta.json"):
        self.index = faiss.read_index(path_index)
        with open(path_meta, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    def query(self, q_vec: np.ndarray, top_k=5):
        if self.index.ntotal == 0:
            return []
        
        faiss.normalize_L2(q_vec)
        actual_k = min(top_k, self.index.ntotal)
        D, I = self.index.search(q_vec, actual_k)
        results=[]
        for scores, idxs in zip(D, I):
            for sc, ix in zip(scores, idxs):
                if ix < 0 or ix >= len(self.metadata): 
                    continue
                m = self.metadata[ix].copy()
                m["score"] = float(sc)
                results.append(m)
        return results

# Example: ingest a file (memory-efficient)
def ingest_file(path, index: FaissIndex, source_id=None):
    """Memory-efficient file ingestion with better chunking"""
    try:
        ext = os.path.splitext(path)[1].lower()
        
        # Extract text
        if ext in [".pdf"]:
            text = extract_text_from_pdf(path)
        elif ext in [".md", ".markdown"]:
            text = extract_text_from_md(path)
        else:
            with open(path, "r", encoding="utf-8", errors='ignore') as f:
                text = f.read()
        
        if len(text.strip()) < 50:
            print(f"⚠️ Document {os.path.basename(path)} trop petit, ignoré")
            return
        
        # Normalize and chunk with better params
        text = normalize_text(text)
        chunks = chunk_text(text, max_tokens=600, overlap_tokens=100)
        
        if not chunks:
            print(f"⚠️ Aucun chunk généré pour {os.path.basename(path)}")
            return
        
        # Process in batches
        BATCH_SIZE = 20  # Process 20 chunks at a time
        for i in range(0, len(chunks), BATCH_SIZE):
            batch_chunks = chunks[i:i + BATCH_SIZE]
            texts = [c["text"] for c in batch_chunks]
            
            # Embed batch
            vecs = embed_texts(texts, batch_size=10)
            
            # Create metadata
            metas = [
                {
                    "source": path, 
                    "chunk_id": i + j, 
                    "text": t[:1500]  # Store more text for context
                } 
                for j, t in enumerate(texts)
            ]
            
            # Add to index
            index.add(vecs, metas)
            
            # Free memory
            del vecs, texts, batch_chunks
        
        print(f"✅ Indexé: {os.path.basename(path)} ({len(chunks)} chunks)")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'indexation de {os.path.basename(path)}: {e}")
