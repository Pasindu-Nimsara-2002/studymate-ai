import os
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide"
)

UPLOAD_DIR = "data/uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.title("📚 StudyMate AI")
st.write("Upload your lecture notes and ask questions using AI.")

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

    with st.expander("Preview first chunk"):
        if len(chunks) > 0:
            st.write(chunks[0].page_content)
            st.write(chunks[0].metadata)