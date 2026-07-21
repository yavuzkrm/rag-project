import chromadb
from config import CHROMA_PATH

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="rag_collection")

def create_chroma_collection(chunks):

    if not chunks:
        return
   
    start_index = collection.count()

    document = [chunk.page_content for chunk in chunks]
    metadata = [chunk.metadata for chunk in chunks]
    ids = [str(start_index + i) for i in range(len(chunks))]

    collection.add(
        documents=document,
        metadatas=metadata,
        ids=ids
    )

def search_similar_chunks(query, n_results=3):
    result = collection.query(
        query_texts = [query],
        n_results = n_results
    )

    return result

def check_chunks_source_exists():
    existing_collections = collection.get()
    indexed_sources = set()

    for data in existing_collections['metadatas']:
        indexed_sources.add(data['source'])

    return indexed_sources
