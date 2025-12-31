from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_and_chunk_pdfs(pdf_paths, chunk_size=1000, chunk_overlap=200):
    all_docs = []
    for path in pdf_paths:
        loader = PyPDFLoader(path)
        raw_docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = splitter.split_documents(raw_docs)
        all_docs.extend(chunks)
    return all_docs
