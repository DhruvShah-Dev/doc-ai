from document_store.quality import describe_text


def test_empty_extraction_is_not_indexable():
    assert describe_text("")["has_usable_text"] is False
    assert describe_text("Page 1:\n")["has_usable_text"] is False


def test_readable_text_is_reported():
    quality = describe_text("This example contains enough readable text for indexing.")
    assert quality["has_usable_text"] is True
    assert quality["words"] == 8
