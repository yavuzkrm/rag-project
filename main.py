import os
import streamlit as st
from document_loader_chunker import load_and_chunk_documents
from vektor_store import create_chroma_collection, search_similar_chunks, check_chunks_source_exists, collection
from llm_client import generate_response
from config import DATA_PATH

st.set_page_config(page_title="Kişisel Bilgi Dağarcığı", page_icon="📚")

st.title("📚 Kişisel Bilgi Dağarcığı")
st.caption("Yüklenilen dosyalara göre soru sorabilirsin.")


def run_indexing():
    """Yeni dosyaları tara ve ChromaDB'ye ekle."""
    existing_sources = check_chunks_source_exists()
    chunks = load_and_chunk_documents(existing_sources)
    create_chroma_collection(chunks)
    return len(chunks)

# --- İlk açılışta bir kere indexle ---
if "indexed" not in st.session_state:
    with st.spinner("Belgeler taranıyor, yeni olanlar indexleniyor..."):
        new_count = run_indexing()
        st.session_state["indexed"] = True
    if new_count:
        st.success(f"{new_count} yeni chunk indexlendi.")
    else:
        if collection.count() == 0:
            st.info("Herhangi bir dosya bulunmamakta.")
        else:
            st.info("Yeni dosya yok, mevcut veriler kullanılıyor.")

# --- Konuşma geçmişi ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --- Soru girişi ---
user_input = st.chat_input("Sorunu yaz...")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Düşünüyor..."):
            # Şu anki soru hariç, önceki mesajları geçmiş olarak gönder
            history = st.session_state["messages"][:-1]

            result = search_similar_chunks(user_input, n_results=3)
            answer = generate_response(user_input, result, history=history)
            st.markdown(answer)

            sources = set()
            for metadata_list in result.get("metadatas", []):
                for metadata in metadata_list:
                    sources.add(metadata.get("source", "bilinmiyor"))

            if sources:
                with st.expander("Kaynaklar"):
                    for source in sources:
                        st.write(f"- {source}")

    st.session_state["messages"].append({"role": "assistant", "content": answer})


# --- Yan panel: dosya yükleme + sohbeti temizle ---
with st.sidebar:
    st.header("Dosya Ekle")

    uploaded_files = st.file_uploader(
        "PDF, DOCX veya TXT yükle",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("Yükle ve indexle"):
            os.makedirs(DATA_PATH, exist_ok=True)

            for uploaded_file in uploaded_files:
                save_path = os.path.join(DATA_PATH, uploaded_file.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            with st.spinner("Yeni dosyalar indexleniyor..."):
                new_count = run_indexing()

            st.success(f"{new_count} yeni chunk indexlendi.")

    st.divider()
    st.header("Ayarlar")
    if st.button("Sohbeti temizle"):
        st.session_state["messages"] = []
        st.rerun()