
import pytest

from app.services.chunking import chunk_text


def test_empty_text_returns_no_chunks():
    result = chunk_text("")

    assert result == []


def test_short_text_returns_one_chunk():
    text = "Python is useful for AI application development."

    result = chunk_text(text)

    assert len(result) == 1
    assert result[0] == text


def test_text_is_split_into_correct_chunk_count():
    text = " ".join(f"word{i}" for i in range(450))

    result = chunk_text(
        text,
        chunk_size=200,
        overlap=40
    )

    assert len(result) == 3
    assert len(result[0].split()) == 200
    assert len(result[1].split()) == 200
    assert len(result[2].split()) == 130


def test_adjacent_chunks_have_expected_overlap():
    text = "one two three four five six seven eight nine ten"

    result = chunk_text(
        text,
        chunk_size=4,
        overlap=1
    )

    assert result == [
        "one two three four",
        "four five six seven",
        "seven eight nine ten"
    ]


def test_invalid_chunk_size_raises_error():
    with pytest.raises(ValueError):
        chunk_text("Some text", chunk_size=0)


def test_negative_overlap_raises_error():
    with pytest.raises(ValueError):
        chunk_text("Some text", chunk_size=4, overlap=-1)


def test_overlap_equal_to_chunk_size_raises_error():
    with pytest.raises(ValueError):
        chunk_text("Some text", chunk_size=4, overlap=4)
