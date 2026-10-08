from app.services.rag.chunking import chunk_document, split_into_sentences


class TestChunking:
    def test_splits_into_sentences(self):
        text = "Dengue is viral. It spreads via mosquitoes. Prevention matters."
        sentences = split_into_sentences(text)
        assert len(sentences) == 3
        assert sentences[0] == "Dengue is viral."

    def test_chunk_document_respects_max_size(self, sample_health_text):
        chunks = chunk_document(sample_health_text, source_id="who-dengue-fact-sheet", max_chunk_chars=150)
        assert len(chunks) > 1
        for chunk in chunks:
            # allow slight overflow since we never split mid-sentence
            assert len(chunk.text) < 300

    def test_chunk_document_preserves_source_id(self, sample_health_text):
        chunks = chunk_document(sample_health_text, source_id="icmr-doc-1")
        assert all(c.source_id == "icmr-doc-1" for c in chunks)

    def test_chunk_document_sequential_indices(self, sample_health_text):
        chunks = chunk_document(sample_health_text, source_id="src", max_chunk_chars=150)
        indices = [c.chunk_index for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_chunk_document_empty_text_returns_empty(self):
        chunks = chunk_document("", source_id="empty")
        assert chunks == []

    def test_chunk_document_carries_metadata(self, sample_health_text):
        chunks = chunk_document(sample_health_text, source_id="src", metadata={"publisher": "WHO"})
        assert all(c.metadata.get("publisher") == "WHO" for c in chunks)

    def test_overlap_preserves_context_continuity(self, sample_health_text):
        chunks = chunk_document(sample_health_text, source_id="src", max_chunk_chars=150, overlap_sentences=1)
        if len(chunks) > 1:
            # last sentence of chunk N should reappear as first of chunk N+1
            last_sentence_of_first = split_into_sentences(chunks[0].text)[-1]
            assert last_sentence_of_first in chunks[1].text
