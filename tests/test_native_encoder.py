"""Opt-in integration tests using the real pinned ONNX model on CPU."""
import os
import unittest

import numpy as np
from tokenizers import Tokenizer

from eninca_documents import Document, OnnxEncoder


@unittest.skipUnless(os.environ.get("ENINCA_DOCUMENT_MODEL"), "Set ENINCA_DOCUMENT_MODEL to run real-model checks")
class NativeEncoderContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.encoder = OnnxEncoder(os.environ["ENINCA_DOCUMENT_MODEL"], batch_size=3, threads=2)

    def test_long_unicode_document_keeps_every_token(self):
        document = Document("unicode", "Préambule 📁. " + "Facture réglée à réception. " * 80 + " FIN DU DOSSIER.")
        metadata, windows = self.encoder.chunks([document])
        self.assertGreater(len(windows), 1)
        tokenizer = Tokenizer.from_str(self.encoder.tokenizer.to_str())
        tokenizer.no_truncation()
        full = tokenizer.encode(document.text, add_special_tokens=False)
        reconstructed = windows[0].ids[1:-1]
        for window in windows[1:]:
            reconstructed.extend(window.ids[1 + self.encoder.identity["stride"]:-1])
        self.assertEqual(reconstructed, full.ids)
        self.assertEqual(metadata[-1].end, len(document.text))
        self.assertTrue(all(0 <= c.start < c.end <= len(document.text) for c in metadata))

    def test_batching_and_length_sort_preserve_embeddings_and_order(self):
        documents = [Document("long", "Les dossiers doivent être archivés et classés. " * 25),
                     Document("short", "Bonjour."), Document("other", "Facture de matériel informatique.")]
        self.encoder.sort_by_length = False
        self.encoder.batch_size = 1
        reference = self.encoder.encode_documents(documents)
        self.encoder.sort_by_length = True
        self.encoder.batch_size = 3
        result = self.encoder.encode_documents(documents)
        self.assertEqual(result.chunks, reference.chunks)
        np.testing.assert_allclose(result.vectors, reference.vectors, atol=3e-5, rtol=3e-5)
        np.testing.assert_allclose(np.linalg.norm(result.vectors, axis=1), 1., atol=1e-6)

    def test_query_is_not_silently_truncated(self):
        with self.assertRaisesRegex(ValueError, "shorten"):
            self.encoder.encode_query("Une longue question concernant les factures. " * 80)


if __name__ == "__main__":
    unittest.main()
