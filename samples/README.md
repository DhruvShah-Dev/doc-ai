# Extraction quality example

Upload `sample_document.txt` through the local app to see the `extraction_quality` object in the upload response. It reports character count, word count, replacement characters, and whitespace percentage. The example contains no private documents or model output.

The upload endpoint rejects files with fewer than three words or twenty visible characters after extraction. A scanned PDF with no extractable text receives a 422 response and needs OCR before indexing. These are intake checks, not a claim that the extracted text is accurate or complete.
