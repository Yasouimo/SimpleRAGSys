# file: app.py
import streamlit as st
from indexer import FaissIndex, ingest_file
from rag_query import answer_question
import os, tempfile
import subprocess
import time
import requests
import gc

st.set_page_config(page_title="RAG Chat (local, Ollama+Gemma)")

def check_ollama_running():
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        return resp.status_code == 200
    except:
        return False

def check_model_exists(model_name="gemma:2b"):
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            return any(model_name in m.get("name", "") for m in models)
    except:
        pass
    return False

@st.cache_resource
def ensure_ollama_ready():
    if not check_ollama_running():
        st.info("🚀 Démarrage d'Ollama...")
        try:
            subprocess.Popen(["ollama", "serve"], 
                           shell=True,
                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            max_wait = 10
            for i in range(max_wait):
                time.sleep(1)
                if check_ollama_running():
                    st.success("✅ Ollama démarré!")
                    break
            else:
                st.error("❌ Impossible de démarrer Ollama. Démarrez-le manuellement: `ollama serve`")
                return False
        except Exception as e:
            st.error(f"❌ Erreur lors du démarrage d'Ollama: {e}")
            return False
    
    if not check_model_exists("gemma:2b"):
        st.warning("⚠️ Le modèle gemma:2b n'est pas installé.")
        if st.button("📥 Télécharger gemma:2b (1.7 GB)"):
            with st.spinner("Téléchargement du modèle..."):
                try:
                    subprocess.run(["ollama", "pull", "gemma:2b"], check=True)
                    st.success("✅ Modèle gemma:2b installé!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
        st.info("Ou exécutez manuellement: `ollama pull gemma:2b`")
        return False
    
    return True

ollama_ready = ensure_ollama_ready()

if not ollama_ready:
    st.stop()

# Load or create index
INDEX_PATH = "index.faiss"
META_PATH = "meta.json"

# Add session state to track if we need to reload
if 'index_loaded' not in st.session_state:
    st.session_state.index_loaded = False
    st.session_state.idx = None

# NEW: Track processed uploaded files to prevent re-indexing
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = set()

if not st.session_state.index_loaded or st.session_state.idx is None:
    if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
        idx = FaissIndex()
        idx.load(INDEX_PATH, META_PATH)
        st.session_state.idx = idx
    else:
        idx = FaissIndex(dim=384)
        st.session_state.idx = idx
    st.session_state.index_loaded = True
else:
    idx = st.session_state.idx

st.title("RAG Chat (Ollama gemma:2b)")

st.sidebar.caption("💾 Optimisé pour 8GB RAM")

with st.sidebar:
    st.success("🟢 Ollama actif")
    st.caption("Modèle: gemma:2b")

selected_demo = None

with st.expander("🧪 Tester avec des questions exemple"):
    if idx.index.ntotal > 0:
        example_questions = [
            "Quels sont les objectifs du stage?",
            "Quelle méthodologie a été utilisée?",
            "Quelles sont les conclusions principales?",
        ]
        for eq in example_questions:
            if st.button(eq, key=f"demo_{eq}"):
                selected_demo = eq
    else:
        st.info("Indexez d'abord des documents pour tester")

DOCS_FOLDER = "docs/Rapports PFE"
if os.path.exists(DOCS_FOLDER):
    with st.expander("📁 Charger les documents du dossier 'docs/Rapports PFE'", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Réindexer tous les documents", type="primary"):
                # Create fresh index
                idx = FaissIndex(dim=384)
                st.session_state.idx = idx
                
                count = 0
                progress_bar = st.progress(0)
                status_text = st.empty()
                all_files = []
                
                for root, dirs, files in os.walk(DOCS_FOLDER):
                    for file in files:
                        if file.endswith(('.pdf', '.txt', '.md')):
                            all_files.append(os.path.join(root, file))
                
                total_files = len(all_files)
                
                if total_files == 0:
                    st.warning("Aucun document trouvé")
                else:
                    for i, filepath in enumerate(all_files):
                        status_text.text(f"📄 Indexation: {os.path.basename(filepath)}...")
                        try:
                            ingest_file(filepath, idx)
                            count += 1
                            gc.collect()
                        except Exception as e:
                            st.error(f"❌ Erreur {os.path.basename(filepath)}: {e}")
                        
                        progress_bar.progress((i + 1) / total_files)
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    if count > 0:
                        idx.save(INDEX_PATH, META_PATH)
                        st.success(f"✅ {count} documents réindexés!")
                        st.session_state.idx = idx
                        gc.collect()
                        time.sleep(1)
                        st.rerun()
        
        with col2:
            if st.button("🗑️ Supprimer l'index complet"):
                if os.path.exists(INDEX_PATH):
                    os.remove(INDEX_PATH)
                if os.path.exists(META_PATH):
                    os.remove(META_PATH)
                
                # Reset session state
                st.session_state.idx = FaissIndex(dim=384)
                st.session_state.index_loaded = False
                st.session_state.processed_files = set()  # FIXED: Also clear processed files
                
                st.success("✅ Index supprimé!")
                time.sleep(1)
                st.rerun()

st.sidebar.header("📚 Base de documents")
if idx.index.ntotal > 0:
    sources = {}
    for meta in idx.metadata:
        src = meta.get("source", "Unknown")
        sources[src] = sources.get(src, 0) + 1
    
    st.sidebar.metric("Total chunks", idx.index.ntotal)
    st.sidebar.metric("Documents", len(sources))
    
    with st.sidebar.expander("📄 Détails des chunks"):
        for src, count in sources.items():
            st.write(f"**{os.path.basename(src)}**")
            st.caption(f"   → {count} chunks")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Filtrer par document")
    doc_options = ["Tous les documents"] + [os.path.basename(src) for src in sources.keys()]
    selected_doc = st.sidebar.selectbox("Rechercher dans:", doc_options)
    
    if selected_doc != "Tous les documents":
        selected_path = next((src for src in sources.keys() if os.path.basename(src) == selected_doc), None)
        if selected_path:
            st.sidebar.info(f"📍 **{selected_doc}**\n({sources[selected_path]} chunks)")
else:
    st.sidebar.warning("⚠️ Aucun document indexé")
    selected_doc = "Tous les documents"

# FIXED: Upload section with proper handling
with st.expander("📤 Uploader un nouveau document"):
    uploaded = st.file_uploader("PDF / TXT / MD (max 5MB)", type=["pdf","txt","md"])
    if uploaded is not None:
        # Check if file was already processed in this session
        if uploaded.name not in st.session_state.processed_files:
            if uploaded.size > 5_000_000:
                st.error("❌ Fichier trop volumineux (max 5MB)")
            else:
                tf = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1])
                tf.write(uploaded.read())
                tf.flush()
                tf.close()
                
                try:
                    with st.spinner(f"Indexation de {uploaded.name}..."):
                        ingest_file(tf.name, idx)
                        idx.save(INDEX_PATH, META_PATH)
                        
                        # Mark as processed to prevent re-indexing
                        st.session_state.processed_files.add(uploaded.name)
                        st.session_state.idx = idx
                        
                    st.success(f"✅ {uploaded.name} indexé!")
                    gc.collect()
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
                finally:
                    os.unlink(tf.name)
        else:
            st.info(f"Fichier '{uploaded.name}' déjà indexé (rafraîchissez pour uploader un nouveau fichier).")

q = selected_demo if selected_demo else st.text_input("💬 Pose ta question:")

if (st.button("🚀 Envoyer") or selected_demo) and q and q.strip():
    if idx.index.ntotal == 0:
        st.warning("⚠️ Index vide — ajoutez des documents d'abord")
    else:
        with st.spinner("🔍 Recherche en cours..."):
            resp = answer_question(idx, q, top_k=5)
        
        if selected_doc != "Tous les documents":
            filtered_sources = [s for s in resp["sources"] if os.path.basename(s['source']) == selected_doc]
            if not filtered_sources:
                st.warning(f"❌ Aucun résultat dans '{selected_doc}'")
                st.stop()
            resp["sources"] = filtered_sources
            if filtered_sources:
                from rag_query import build_rag_prompt, query_ollama
                filtered_prompt = build_rag_prompt(q, filtered_sources)
                resp["answer"] = query_ollama(filtered_prompt)
        
        st.markdown("### 💬 Réponse")
        if selected_doc != "Tous les documents":
            st.caption(f"📍 Basé sur: **{selected_doc}**")
        st.write(resp["answer"])
        
        st.markdown("### 📊 Sources (par pertinence)")
        st.caption("🟢 >0.7 Très pertinent | 🟡 0.5-0.7 Pertinent | 🟠 <0.5 Peu pertinent")
        
        for i, s in enumerate(resp["sources"], 1):
            score = s['score']
            if score > 0.7:
                emoji = "🟢"
                quality = "Très pertinent"
            elif score > 0.5:
                emoji = "🟡"
                quality = "Pertinent"
            else:
                emoji = "🟠"
                quality = "Peu pertinent"
            
            with st.expander(f"{emoji} **Source {i}**: {os.path.basename(s['source'])} (chunk {s['chunk_id']}) — {score:.3f} ({quality})"):
                st.progress(score)
                st.markdown(f"```\n{s['text'][:400]}...\n```" if len(s['text']) > 400 else f"```\n{s['text']}\n```")
