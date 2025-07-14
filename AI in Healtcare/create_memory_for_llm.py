# Create memory vectorstore from PDF documents
import os
from typing import List
from dotenv import load_dotenv, find_dotenv
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def load_pdf_files(data_path: str) -> List[Document]:
    loader = DirectoryLoader(
        data_path,
        glob="*.pdf",
        loader_cls=lambda path: PyPDFLoader(path)  # Pass a callable that instantiates the loader # type: ignore
    )
    documents = loader.load()
    return documents

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Ensure the vectorstore directory exists
os.makedirs("vectorstore", exist_ok=True)

# Step 1: Load raw PDF documents from data directory
DATA_PATH = "data/"
documents = load_pdf_files(DATA_PATH)
# print("Loaded PDF documents:", len(documents))

# Step 2: Split documents into chunks for embeddings
def create_chunks(docs: List[Document]) -> List[Document]:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)
    return chunks

text_chunks = create_chunks(documents)
# print("Text chunks created:", len(text_chunks))

# Step 3: Initialize embedding model
def get_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

embedding_model = get_embedding_model()

# Step 4: Create and save FAISS vector store
DB_FAISS_PATH = "vectorstore/db_faiss"
db = FAISS.from_documents(text_chunks, embedding_model)
db.save_local(DB_FAISS_PATH)

print(f"✅ Vector store saved to: {DB_FAISS_PATH}")