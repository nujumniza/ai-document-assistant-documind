# Portfolio Project Description

## Short description

DocuMind AI is a full-stack Retrieval-Augmented Generation application that enables users to upload PDF documents, search their content semantically, and ask natural-language questions with source-page evidence.

## Resume / portfolio bullets

- Built a full-stack document intelligence prototype using FastAPI and Streamlit, with PDF ingestion, page-aware chunking, semantic embeddings, and vector search.
- Integrated Sentence Transformers and ChromaDB to index and retrieve relevant document passages using cosine similarity.
- Implemented a RAG pipeline that combines retrieved document context with Groq-hosted LLM generation and returns source metadata for answer traceability.
- Developed document-management workflows for PDF upload, indexed-document listing, and deletion, with essential API, chunking, and prompt-construction tests.

## Interview explanation

**What problem does it solve?**  
Users often have large PDFs that are difficult to search manually. DocuMind AI lets users ask natural-language questions and retrieves relevant passages before generating an answer.

**Why RAG instead of sending the entire PDF to the model?**  
RAG retrieves a smaller set of relevant passages for each question. This reduces irrelevant context and makes it possible to show which source pages informed the answer.

**What is the role of embeddings?**  
Embeddings convert text into numerical vectors so semantically related questions and passages can be compared, even when they do not use exactly the same words.

**Why ChromaDB?**  
It provides persistent vector storage and similarity search with a relatively simple local development setup.

**What are the current limitations?**  
The prototype does not yet pass prior turns into the next question, does not implement authentication or tenant isolation, and needs stronger security, evaluation, and operational controls before production use.

**How would you improve it?**  
Add multi-turn context, evaluate retrieval quality on a labelled dataset, test hybrid retrieval/reranking, add OCR for scanned PDFs, implement authentication and tenant isolation, and use durable managed infrastructure.
