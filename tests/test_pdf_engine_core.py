import pytest

from app.services.pdf_engine.core import (
    PDFEngineError,
    compress_pdf,
    extract_pages,
    get_page_count,
    merge_pdfs,
    rotate_pages,
    split_every_page,
    split_pdf,
)


def test_merge_pdfs(make_pdf):
    merged = merge_pdfs([make_pdf(3), make_pdf(2)])
    assert get_page_count(merged) == 5


def test_merge_requires_at_least_two_files(sample_pdf):
    with pytest.raises(PDFEngineError):
        merge_pdfs([sample_pdf])


def test_split_pdf(sample_pdf):
    parts = split_pdf(sample_pdf, [(1, 1), (2, 3)])
    assert [get_page_count(p) for p in parts] == [1, 2]


def test_split_out_of_range_raises(sample_pdf):
    with pytest.raises(PDFEngineError):
        split_pdf(sample_pdf, [(1, 99)])


def test_split_every_page(sample_pdf):
    parts = split_every_page(sample_pdf)
    assert len(parts) == 3
    assert all(get_page_count(p) == 1 for p in parts)


def test_extract_pages(sample_pdf):
    extracted = extract_pages(sample_pdf, [2])
    assert get_page_count(extracted) == 1


def test_extract_pages_out_of_range_raises(sample_pdf):
    with pytest.raises(PDFEngineError):
        extract_pages(sample_pdf, [99])


def test_rotate_pages(sample_pdf):
    rotated = rotate_pages(sample_pdf, [1], 90)
    assert get_page_count(rotated) == 3


def test_rotate_invalid_degrees_raises(sample_pdf):
    with pytest.raises(PDFEngineError):
        rotate_pages(sample_pdf, [1], 45)


@pytest.mark.parametrize("quality", ["low", "medium", "high"])
def test_compress_pdf(sample_pdf, quality):
    compressed = compress_pdf(sample_pdf, quality)
    assert get_page_count(compressed) == get_page_count(sample_pdf)
    assert len(compressed) > 0


def test_compress_invalid_quality_raises(sample_pdf):
    with pytest.raises(PDFEngineError):
        compress_pdf(sample_pdf, "ultra")
