import os
import streamlit as st
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


load_dotenv()

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide"
)

UPLOAD_DIR = "data/uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.title("📚 StudyMate AI")
st.write("Upload your lecture notes and create a local FAISS vector database.")

uploaded_file = st.file_uploader(
    "Upload a PDF file",
    type=["pdf"]
)

if uploaded_file is not None:
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)

    with open(file_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    st.success(f"PDF uploaded successfully: {uploaded_file.name}")

    with st.spinner("Reading PDF..."):
        loader = PyPDFLoader(file_path)
        documents = loader.load()

    st.write(f"Number of pages loaded: {len(documents)}")

    with st.spinner("Splitting text into chunks..."):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)

    st.write(f"Number of chunks created: {len(chunks)}")

    with st.spinner("Creating local HuggingFace embeddings and FAISS vector store..."):
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            encode_kwargs={"normalize_embeddings": True}
        )

        vectorstore = FAISS.from_documents(chunks, embeddings)

    st.success("FAISS vector store created successfully using local embeddings.")

    query = st.text_input("Test retrieval: ask something from the PDF")

    if query:
        with st.spinner("Retrieving relevant chunks..."):
            results = vectorstore.similarity_search(query, k=4)

        st.subheader("Retrieved Chunks")

        for i, doc in enumerate(results):
            page_number = doc.metadata.get("page", "Unknown")

            if isinstance(page_number, int):
                page_number += 1

            with st.expander(f"Chunk {i + 1} - Page {page_number}"):
                st.write(doc.page_content)