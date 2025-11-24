# file: rag_query.py
import requests, json, numpy as np
from indexer import FaissIndex, MODEL, embed_texts
OLLAMA_GEN_URL = "http://localhost:11434/api/generate"  # endpoint
MODEL_NAME = "gemma:2b"  # as requested

def build_rag_prompt(question, retrieved_chunks):
    header = "Tu es un assistant qui répond en se basant uniquement sur les documents fournis. Si l'information n'est pas dans les documents, dis 'Je ne sais pas'.\n\n"
    docs = "\n\n---\n\n".join([f"[Source: {c['source']} | chunk {c['chunk_id']}]\n{c['text']}" for c in retrieved_chunks])
    prompt = f"{header}Documents:\n{docs}\n\nQuestion: {question}\nRéponse:"
    return prompt

def query_ollama(prompt, model=MODEL_NAME, stream=False):
    payload = {"model": model, "prompt": prompt, "stream": False}
    resp = requests.post(OLLAMA_GEN_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json().get("response") or resp.text

def answer_question(index: FaissIndex, question: str, top_k=4):
    q_vec = embed_texts([question])
    results = index.query(q_vec, top_k=top_k)
    
    # Filter low-quality results
    filtered_results = [r for r in results if r['score'] > 0.3]
    
    if not filtered_results:
        return {
            "answer": "Je ne trouve pas d'information pertinente dans les documents indexés pour répondre à cette question.",
            "sources": results
        }
    
    prompt = build_rag_prompt(question, filtered_results)
    answer = query_ollama(prompt)
    return {"answer": answer, "sources": results}
