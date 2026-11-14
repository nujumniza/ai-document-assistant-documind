
from functools import lru_cache
from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def load_embedding_model():
    """
    Load the model once and reuse it for future requests.
    """
    return SentenceTransformer(MODEL_NAME)


def generate_embeddings(chunks: list[dict]) -> list[dict]:
    """
    Generate one embedding vector for each document chunk.
    Preserve the original chunk metadata.
    """

    if not chunks:
        return []

    model = load_embedding_model()

    # Extract only the text that needs to be converted
    texts = [chunk["text"] for chunk in chunks]

    # Convert all chunk texts into numerical vectors
    vectors = model.encode(
        texts,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    # Attach each vector to its corresponding chunk
    embedded_chunks = []

    for chunk, vector in zip(chunks, vectors):
        embedded_chunk = chunk.copy()
        embedded_chunk["embedding"] = vector.tolist()

        embedded_chunks.append(embedded_chunk)

    return embedded_chunks

def generate_query_embedding(query: str) -> list[float]:
    """
    Convert a user's search question into an embedding.

    Uses the same model and normalization settings
    as the document chunks.
    """
    model = load_embedding_model()

    vector = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return vector.tolist()
