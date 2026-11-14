
def chunk_text(
    text: str,
    chunk_size: int = 200,
    overlap: int = 40
) -> list[str]:
    """
    Divide text into overlapping word-based chunks.

    chunk_size: maximum number of words per chunk.
    overlap: number of words repeated between adjacent chunks.
    """

    # Validate the configuration
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size"
        )

    # Convert the text into individual words
    words = text.split()

    chunks = []
    start = 0

    # Continue until all words have been processed
    while start < len(words):

        end = min(start + chunk_size, len(words))

        # Create one chunk
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        # Stop when we reach the end of the document
        if end == len(words):
            break

        # Move forward, keeping the overlapping words
        start = end - overlap

    return chunks
