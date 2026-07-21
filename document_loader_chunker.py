from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, Docx2txtLoader, TextLoader  # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter # type: ignore
from config import DATA_PATH

def load_and_chunk_documents(existing_sources):
    # Load all documents from the specified data path
    all_documents = []

    pdf_loader = DirectoryLoader(DATA_PATH, glob="**/*.pdf", loader_cls=PyPDFLoader)
    all_documents.extend(pdf_loader.load())

    docx_loader = DirectoryLoader(DATA_PATH, glob="**/*.docx", loader_cls=Docx2txtLoader)
    all_documents.extend(docx_loader.load())

    txt_loader = DirectoryLoader(DATA_PATH, glob="**/*.txt", loader_cls=TextLoader)
    all_documents.extend(txt_loader.load())

    filtered_documents = []
    for document in all_documents:
        if document.metadata['source'] not in existing_sources:
                filtered_documents.append(document)

    # Split the loaded documents into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100, length_function=len, is_separator_regex=False)
    chunks = splitter.split_documents(filtered_documents)

    return chunks