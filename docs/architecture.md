# StudyMate AI Architecture

## Overview

StudyMate AI is a Retrieval-Augmented Generation system that allows users to upload lecture note PDFs and ask questions from the uploaded documents.

The system does not rely only on the general knowledge of the LLM. Instead, it first retrieves relevant content from the uploaded PDFs and then uses that content as context for answer generation.

## Main Pipeline

```text
PDF Upload
    ↓
PDF Text Extraction
    ↓
Text Chunking
    ↓
Embedding Generation
    ↓
FAISS Vector Store
    ↓
User Question
    ↓
Similarity Search
    ↓
Relevant Chunk Retrieval
    ↓
Gemini Answer Generation
    ↓
Answer + Source References