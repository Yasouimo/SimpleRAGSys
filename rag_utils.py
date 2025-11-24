# file: rag_utils.py
import re
import fitz  # PyMuPDF

def extract_text_from_pdf(path):
    txt = []
    try:
        doc = fitz.open(path)
        for page in doc:
            txt.append(page.get_text())
        doc.close()
    except Exception as e:
        print(f"Erreur PDF: {e}")
        return ""
    return "\n".join(txt)

def extract_text_from_md(path):
    # CORRECTION : On lit le fichier brut, sans convertir en HTML
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def normalize_text(s: str) -> str:
    if not s: return ""
    s = s.replace('\r', '\n')
    s = re.sub(r'\n{3,}', '\n\n', s) # Max 2 sauts de ligne
    return s.strip()

def chunk_by_sections(text: str, max_chars=1500) -> list:
    """
    Découpe intelligente :
    1. Essaie de couper par titres (## ou #) pour le Markdown
    2. Si le bloc est trop gros (ou pas de titres comme PDF), coupe par paragraphes
    """
    if not text: return []
    
    chunks = []
    lines = text.split('\n')
    current_chunk = []
    current_header = "Document"
    
    # Regex pour détecter les titres (# Titre ou ## Titre)
    header_pattern = re.compile(r'^(#{1,3})\s+(.+)$')

    for line in lines:
        match = header_pattern.match(line.strip())
        if match:
            # On sauvegarde le chunk précédent
            if current_chunk:
                text_block = "\n".join(current_chunk).strip()
                if text_block:
                    chunks.append({"text": f"**Contexte: {current_header}**\n\n{text_block}"})
            
            # Nouveau contexte
            current_header = match.group(2)
            current_chunk = []
        else:
            current_chunk.append(line)
            
    # Ajouter le dernier morceau
    if current_chunk:
        text_block = "\n".join(current_chunk).strip()
        if text_block:
            chunks.append({"text": f"**Contexte: {current_header}**\n\n{text_block}"})

    # Post-traitement : Si un chunk est ENCORE trop gros (cas des PDF sans titres)
    final_chunks = []
    for chunk in chunks:
        if len(chunk["text"]) > max_chars:
            # On recoupe par paragraphes (double saut de ligne)
            paragraphs = chunk["text"].split('\n\n')
            buffer = ""
            for p in paragraphs:
                if len(buffer) + len(p) < max_chars:
                    buffer += p + "\n\n"
                else:
                    final_chunks.append({"text": buffer.strip()})
                    buffer = p + "\n\n"
            if buffer:
                final_chunks.append({"text": buffer.strip()})
        else:
            final_chunks.append(chunk)

    return final_chunks

def chunk_text(text: str, max_tokens=300, overlap_tokens=0, approx_chars_per_token=4):
    # On ignore overlap_tokens ici car on préfère la cohérence des sections
    return chunk_by_sections(text, max_chars=max_tokens * approx_chars_per_token)