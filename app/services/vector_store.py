
from pathlib import Path

import chromadb


# Find the project root directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Store the vector database inside the project.
DATA_DIR = Path(
    os.getenv("DATA_DIR", str(PROJECT_ROOT / "data"))
)
CHROMA_PATH = DATA_DIR / "chroma"


def get_collection():
    """
    Create or retrieve the persistent ChromaDB collection.
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
    filename: str,
    organisation_id: str | None = None
) -> int:
    """
    Store document chunks, embeddings and metadata.

    organisation_id is optional:
    - DocuMind documents can omit it.
    - ResolveIQ documents should provide it.
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

        metadata = {
            "document_id": document_id,
            "filename": filename,
            "page_number": chunk["page_number"],
            "chunk_index": chunk["chunk_index"],
            "word_count": chunk["word_count"]
        }

        # Add organisation metadata for ResolveIQ documents.
        if organisation_id:
            metadata["organisation_id"] = organisation_id

        metadatas.append(metadata)

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
    document_id: str | None = None,
    organisation_id: str | None = None
) -> list[dict]:
    """
    Search ChromaDB for relevant document chunks.

    Optional filters:
    - document_id: search one specific document.
    - organisation_id: search one organisation's documents.

    Both filters can be applied together.
    """

    collection = get_collection()

    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    result_limit = min(top_k, total_chunks)

    # Build metadata filters.
    filters = []

    if document_id:
        filters.append({
            "document_id": document_id
        })

    if organisation_id:
        filters.append({
            "organisation_id": organisation_id
        })

    where_filter = None

    if len(filters) == 1:
        where_filter = filters[0]

    elif len(filters) > 1:
        where_filter = {
            "$and": filters
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


def list_documents(
    organisation_id: str | None = None
):
    """
    Return a summary of indexed documents.

    If organisation_id is provided, return only
    documents belonging to that organisation.
    """

    collection = get_collection()

    if organisation_id:
        result = collection.get(
            where={
                "organisation_id": organisation_id
            },
            include=["metadatas"]
        )
    else:
        result = collection.get(
            include=["metadatas"]
        )

    documents = {}

    for metadata in result["metadatas"]:

        document_id = metadata.get("document_id")

        if not document_id:
            continue

        if document_id not in documents:
            documents[document_id] = {
                "document_id": document_id,
                "filename": metadata.get(
                    "filename",
                    "Unknown"
                ),
                "total_chunks": 0,
                "pages": set()
            }

        documents[document_id]["total_chunks"] += 1

        page_number = metadata.get("page_number")

        if page_number is not None:
            documents[document_id]["pages"].add(page_number)

    for document in documents.values():
        document["total_pages"] = len(document["pages"])
        del document["pages"]

    return list(documents.values())


def delete_document(
    document_id: str,
    organisation_id: str | None = None
):
    """
    Delete all chunks belonging to a document.

    If organisation_id is provided, deletion is
    restricted to that organisation.
    """

    collection = get_collection()

    filters = [
        {
            "document_id": document_id
        }
    ]

    if organisation_id:
        filters.append({
            "organisation_id": organisation_id
        })

    if len(filters) == 1:
        where_filter = filters[0]
    else:
        where_filter = {
            "$and": filters
        }

    existing = collection.get(
        where=where_filter,
        include=["metadatas"]
    )

    chunk_count = len(existing["ids"])

    if chunk_count == 0:
        return 0

    collection.delete(
        where=where_filter
    )

    return chunk_count
