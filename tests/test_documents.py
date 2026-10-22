"""Functional contracts, without model download or network access."""
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from eninca_documents.core import (Chunk, Corpus, Document, PrototypeClassifier,
                                    classification_metrics, read_jsonl, unit_rows)
from eninca_documents.encoder import mean_pool


def corpus(documents, vectors, identity=None):
    return Corpus(documents, [Chunk(d.id, 0, 0, len(d.text), 4) for d in documents],
                  np.asarray(vectors, np.float32), identity or {"model": "unit-test-fixture"})


class DocumentContracts(unittest.TestCase):
    def test_empty_text_and_duplicate_ids_are_rejected(self):
        for text in ("", " \n\t", "\u00a0"):
            with self.assertRaises(ValueError):
                Document("x", text)
        with self.assertRaises(ValueError):
            corpus([Document("x", "abc"), Document("x", "def")], [[1, 0], [0, 1]])

    def test_input_retains_accents_and_whitespace(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "docs.jsonl"
            text = "  Réclamation 📁 : pièce jointe.\n"
            path.write_text(json.dumps({"id": "d", "text": text}) + "\n", encoding="utf-8")
            self.assertEqual(read_jsonl(path)[0].text, text)
            path.write_text('{"id":"d","text":"test","secret":5}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "line 1"):
                read_jsonl(path)

    def test_mean_pool_excludes_padding(self):
        hidden = np.array([[[2., 4.], [4., 6.], [1e6, 1e6]]], dtype=np.float32)
        np.testing.assert_array_equal(mean_pool(hidden, np.array([[1, 1, 0]])), [[3., 5.]])
        with self.assertRaises(ValueError):
            mean_pool(hidden, np.zeros((1, 3)))

    def test_invalid_embeddings(self):
        for value in ([[0., 0.]], [[np.nan, 1.]], [[np.inf, 1.]], []):
            with self.assertRaises(ValueError):
                unit_rows(value)

    def test_search_deduplicates_documents_and_retains_best_span(self):
        documents = [Document("a", "first second"), Document("b", "other")]
        chunks = [Chunk("a", 0, 0, 5, 3), Chunk("a", 1, 6, 12, 3), Chunk("b", 0, 0, 5, 3)]
        index = Corpus(documents, chunks, [[.8, .6], [1, 0], [.6, .8]], {"model": "fixture"})
        hits = index.search([1, 0], encoder_identity=index.encoder_identity, top_k=2)
        self.assertEqual([h["document_id"] for h in hits], ["a", "b"])
        self.assertEqual(hits[0]["excerpt"], "second")
        with self.assertRaises(ValueError):
            index.search([1, 0], encoder_identity={"model": "changed"})

    def test_search_ties_have_stable_document_order(self):
        index = corpus([Document("b", "B"), Document("a", "A")], [[1, 0], [1, 0]])
        hits = index.search([1, 0], encoder_identity=index.encoder_identity)
        self.assertEqual([h["document_id"] for h in hits], ["a", "b"])

    def test_missing_or_invalid_chunks_fail(self):
        documents = [Document("a", "text"), Document("b", "more")]
        for chunk in (Chunk("a", 1, 0, 4, 3), Chunk("a", 0, 0, 50, 3), Chunk("unknown", 0, 0, 4, 3)):
            with self.assertRaises(ValueError):
                Corpus(documents, [chunk], [[1, 0]], {})

    def test_export_roundtrip_and_corruption_detection(self):
        index = corpus([Document("a", "Texte à conserver")], [[3, 4]])
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "index"
            index.save(destination)
            recovered = Corpus.load(destination)
            self.assertEqual(recovered.documents, index.documents)
            np.testing.assert_allclose(recovered.vectors, index.vectors, atol=1e-7)
            with self.assertRaises(FileExistsError):
                index.save(destination)
            record_path = destination / "index.json"
            record = json.loads(record_path.read_text())
            record["documents"][0]["text"] = "Texte modifié"
            record_path.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "text checksum"):
                Corpus.load(destination)
            record["documents"][0]["text"] = index.documents[0].text
            record_path.write_text(json.dumps(record))
            with (destination / "vectors.npy").open("ab") as stream:
                stream.write(b"changed")
            with self.assertRaisesRegex(ValueError, "Vector file checksum"):
                Corpus.load(destination)

    def test_classification_and_abstention(self):
        training = corpus([Document("a", "Invoice", "finance"), Document("b", "Holiday", "hr")], [[1, 0], [0, 1]])
        test = corpus([Document("c", "New bill", "finance"), Document("d", "Ambiguous", "hr")], [[1, 0], [1, 1]])
        classifier = PrototypeClassifier(training)
        predictions = classifier.predict(test, min_margin=.05)
        self.assertEqual(predictions[0]["label"], "finance")
        self.assertIsNone(predictions[1]["label"])
        self.assertTrue(predictions[1]["needs_review"])
        metrics = classification_metrics(test.documents, predictions)
        self.assertEqual(metrics["coverage"], .5)
        self.assertEqual(metrics["accuracy_accepted"], 1.)
        self.assertEqual(metrics["accuracy_with_abstentions_as_errors"], .5)
        self.assertEqual(metrics["macro_f1_with_abstentions_as_errors"], .5)

    def test_training_leakage_and_encoder_mismatch_fail(self):
        training = corpus([Document("a", "Invoice", "finance"), Document("b", "Holiday", "hr")], [[1, 0], [0, 1]])
        classifier = PrototypeClassifier(training)
        for document in (Document("a", "Changed"), Document("new", "Invoice")):
            with self.assertRaisesRegex(ValueError, "overlap"):
                classifier.predict(corpus([document], [[1, 0]]))
        with self.assertRaises(ValueError):
            classifier.predict(corpus([Document("c", "Unknown")], [[1, 0]], {"model": "different"}))

    def test_no_accepted_predictions_has_no_defined_accuracy(self):
        documents = [Document("a", "sample", "finance")]
        metrics = classification_metrics(documents, [{"document_id": "a", "label": None}])
        self.assertEqual(metrics["coverage"], 0.)
        self.assertIsNone(metrics["accuracy_accepted"])


if __name__ == "__main__":
    unittest.main()
