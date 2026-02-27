import os
import streamlit as st

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
    st.write(f"Saved path: `{file_path}`")