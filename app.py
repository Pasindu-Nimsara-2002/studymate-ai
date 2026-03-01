import os
import streamlit as st
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import RetrievalQA
from langchain_classic.prompts import PromptTemplate


# Load environment variables
load_dotenv()


# -----------------------------
# App configuration
# -----------------------------
st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide"
)


# -----------------------------
# Constants
# -----------------------------
UPLOAD_DIR = "data/uploaded_pdfs"
VECTOR_DIR = "vectorstore/faiss_index"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("vectorstore", exist_ok=True)


# -----------------------------
# API key validation
# -----------------------------
google_api_key = os.getenv("GOOGLE_API_KEY")
gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
embedding_model = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "models/gemini-embedding-001"
)

if not google_api_key:
    st.error("GOOGLE_API_KEY is missing. Please add it to your .env file.")
    st.stop()


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("📚 StudyMate AI")
st.sidebar.write("RAG-based lecture notes assistant")

st.sidebar.markdown("""
### How it works
1. Upload PDF lecture notes  
2. Extract text from PDF  
3. Split text into chunks  
4. Convert chunks into embeddings  
5. Store embeddings in FAISS  
6. Retrieve relevant chunks  
7. Generate an answer using Gemini  
""")

st.sidebar.markdown("---")
st.sidebar.write("**Current model:**")
st.sidebar.code(gemini_model)


# -----------------------------
# Session state
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "processed_files" not in st.session_state:
    st.session_state.processed_files = []


# -----------------------------
# Main UI
# -----------------------------
st.title("📚 StudyMate AI")
st.write(
    "Upload your lecture notes and ask questions using "
    "Retrieval-Augmented Generation."
)

uploaded_files = st.file_uploader(
    "Upload one or more PDF files",
    type=["pdf"],
    accept_multiple_files=True
)


# -----------------------------
# Process uploaded PDFs
# -----------------------------
if uploaded_files:
    documents = []
    uploaded_file_names = [file.name for file in uploaded_files]

    # Only process again if new files are uploaded
    if uploaded_file_names != st.session_state.processed_files:
        with st.spinner("Processing uploaded PDF files..."):
            for uploaded_file in uploaded_files:
                file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)

                with open(file_path, "wb") as file:
                    file.write(uploaded_file.getbuffer())

                loader = PyPDFLoader(file_path)
                loaded_docs = loader.load()
                documents.extend(loaded_docs)

        st.success(f"Uploaded and loaded {len(uploaded_files)} PDF file(s).")
        st.write(f"Total pages loaded: {len(documents)}")

        # -----------------------------
        # Text chunking
        # -----------------------------
        with st.spinner("Splitting documents into chunks..."):
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(documents)

        st.write(f"Total chunks created: {len(chunks)}")

        # -----------------------------
        # Embeddings + FAISS
        # -----------------------------
        with st.spinner("Creating embeddings and FAISS vector store..."):
            embeddings = GoogleGenerativeAIEmbeddings(
                model=embedding_model
            )

            vectorstore = FAISS.from_documents(chunks, embeddings)

            # Save locally
            vectorstore.save_local(VECTOR_DIR)

            # Store in session state
            st.session_state.vectorstore = vectorstore
            st.session_state.processed_files = uploaded_file_names

        st.success("Vector store created and saved successfully.")

    else:
        st.info("These files are already processed. You can ask questions below.")


# -----------------------------
# Question answering
# -----------------------------
if st.session_state.vectorstore is not None:
    st.markdown("---")
    st.subheader("Ask a question")

    question = st.text_input(
        "Enter your question from the uploaded PDF:"
    )

    if question:
        with st.spinner("Generating answer..."):
            llm = ChatGoogleGenerativeAI(
                model=gemini_model,
                temperature=0
            )

            retriever = st.session_state.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            )

            custom_prompt = PromptTemplate(
                template="""
You are a helpful study assistant. Use only the provided context to answer the question.

If the answer is not available in the context, say:
"I could not find this information in the uploaded document."

Context:
{context}

Question:
{question}

Answer:
""",
                input_variables=["context", "question"]
            )

            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": custom_prompt}
            )

            result = qa_chain.invoke({"query": question})

        answer = result["result"]
        source_documents = result["source_documents"]

        # Save chat history
        st.session_state.chat_history.append({
            "question": question,
            "answer": answer
        })

        # Display answer
        st.subheader("Answer")
        st.write(answer)

        # Display sources
        st.subheader("Sources")

        for i, doc in enumerate(source_documents):
            page_number = doc.metadata.get("page", "Unknown")

            if isinstance(page_number, int):
                page_number = page_number + 1

            source_file = doc.metadata.get("source", "Unknown file")

            with st.expander(f"Source {i + 1} - Page {page_number}"):
                st.write(f"**File:** {source_file}")
                st.write(doc.page_content[:1000])


# -----------------------------
# Chat history
# -----------------------------
if st.session_state.chat_history:
    st.markdown("---")
    st.subheader("Chat History")

    for chat in reversed(st.session_state.chat_history):
        with st.expander(chat["question"]):
            st.write(chat["answer"])
else:
    st.info("Upload PDF files to start asking questions.")