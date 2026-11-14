
from pathlib import Path

import chromadb


# Find the project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Store the vector database inside the project
CHROMA_PATH = PROJECT_ROOT / "data" / "chroma"


def get_collection():
    """
    Create or retrieve the persistent ChromaDB collection.

    PersistentClient saves the database on disk,
    so the vectors remain available after restarting
    the FastAPI application.
    """

    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    collection = client.get_or_create_collection(
        name="document_chunks",
        metadata={
            "hnsw:space": "cosine"
        },
        embedding_function=None
    )

    return collection


def store_chunks(
    embedded_chunks: list[dict],
    document_id: str,
    filename: str
) -> int:
    """
    Store document chunks, embeddings and metadata
    in ChromaDB.

    Returns the number of stored chunks.
    """

    if not embedded_chunks:
        return 0

    collection = get_collection()

    ids = []
    documents = []
    embeddings = []
    metadatas = []

    for chunk in embedded_chunks:

        ids.append(chunk["chunk_id"])

        documents.append(chunk["text"])

        embeddings.append(chunk["embedding"])

        metadatas.append({
            "document_id": document_id,
            "filename": filename,
            "page_number": chunk["page_number"],
            "chunk_index": chunk["chunk_index"],
            "word_count": chunk["word_count"]
        })

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(ids)

def search_chunks(
    query_embedding: list[float],
    top_k: int = 3,
    document_id: str | None = None
) -> list[dict]:
    """
    Search ChromaDB for the most relevant document chunks.

    query_embedding: embedding of the user's question.
    top_k: maximum number of results.
    document_id: optional filter to search one document only.
    """

    collection = get_collection()

    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    # Do not request more results than the collection contains.
    result_limit = min(top_k, total_chunks)

    # Optional filter: search within one uploaded document.
    where_filter = None

    if document_id:
        where_filter = {
            "document_id": document_id
        }

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=result_limit,
        where=where_filter,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    matches = []

    # ChromaDB returns nested lists because a query
    # can contain multiple search questions.
    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for chunk_id, document, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances
    ):
        matches.append({
            "chunk_id": chunk_id,
            "text": document,
            "metadata": metadata,
            "distance": distance
        })

    return matches

def list_documents():
    """
    Return a summary of all documents stored in ChromaDB.
    Each document may contain multiple indexed chunks.
    """
    collection = get_collection()

    result = collection.get(include=["metadatas"])

    documents = {}

    for metadata in result["metadatas"]:
        document_id = metadata.get("document_id")

        if not document_id:
            continue

        if document_id not in documents:
            documents[document_id] = {
                "document_id": document_id,
                "filename": metadata.get("filename", "Unknown"),
                "total_chunks": 0,
                "pages": set()
            }

        documents[document_id]["total_chunks"] += 1

        page_number = metadata.get("page_number")
        if page_number is not None:
            documents[document_id]["pages"].add(page_number)

    # Convert sets into JSON-compatible values.
    for document in documents.values():
        document["total_pages"] = len(document["pages"])
        del document["pages"]

    return list(documents.values())


def delete_document(document_id: str):
    """
    Delete all indexed chunks belonging to one document.
    Return the number of chunks deleted.
    """
    collection = get_collection()

    existing = collection.get(
        where={"document_id": document_id},
        include=["metadatas"]
    )

    chunk_count = len(existing["ids"])

    if chunk_count == 0:
        return 0

    collection.delete(
        where={"document_id": document_id}
    )

    return chunk_count
