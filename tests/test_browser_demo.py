"""Workflow contracts for the local UI; synthetic vectors do not measure quality."""
import copy
import csv
import http.client
from http.server import ThreadingHTTPServer
import io
import json
from pathlib import Path
import tempfile
import threading
import unittest

import numpy as np

from demo.app import Conflict, Demo, Reviews, cached_corpus
from demo.server import handler_for
from eninca_documents.core import Chunk, Corpus, Document


def fixture(state_dir):
    app = Demo("unused", state_dir)
    docs = [Document("a", "A public example", "A"), Document("b", "Another example", "B")]
    app.metadata = {d.id: dict(title="=unsafe title" if d.id == "a" else d.text,
                              source_url="https://www.service-public.gouv.fr/", source_modified="2026") for d in docs}
    app.documents = {d.id: d for d in docs}
    app.labels = ["A", "B"]
    app.predictions = {d.id: dict(document_id=d.id, suggested_label="A", label="A" if d.id == "a" else None,
                                 needs_review=d.id == "b", cosine_score=.8, margin=.02) for d in docs}
    app.search_corpus = Corpus(docs, [Chunk(d.id, 0, 0, len(d.text), 4) for d in docs],
                               np.array([[1., 0.], [0., 1.]]), {"test": True})
    app.scope = "fixture-v1"
    app.reviews = Reviews(Path(state_dir) / "reviews.sqlite3", app.scope)
    app.metrics, app.policy = {"accepted": 1}, {"mode": "thresholds", "min_score": .7, "min_margin": .01}
    app.cache_hits, app.encoding_times = {"test": True}, {"test": 1.}
    app.preparation_seconds, app.search_count, app.search_seconds = 1., 0, 0.
    app.ready = True
    return app


class BrowserWorkflow(unittest.TestCase):
    def test_review_persistence_conflict_undo_and_scope_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = fixture(tmp)
            frozen = copy.deepcopy(app.predictions)
            app.review("a", "B", 0)
            app.review("b", "out_of_scope", 0)
            self.assertEqual(app.snapshot()["review_counts"], dict(completed=2, remaining=0, changed_suggestion=2, outside=1))
            self.assertEqual(fixture(tmp).snapshot()["rows"][0]["review"]["label"], "B")
            with self.assertRaises(Conflict):
                app.review("a", "A", 0)
            app.review("a", None, 1)
            self.assertEqual(app.snapshot()["review_counts"]["remaining"], 1)
            self.assertEqual(app.predictions, frozen)
            self.assertEqual(app.metrics, {"accepted": 1})
            self.assertEqual(Reviews(Path(tmp) / "reviews.sqlite3", "different-model").rows(), {})

    def test_export_retains_abstention_and_prevents_formula_interpretation(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = fixture(tmp)
            app.review("b", "B", 0)
            rows = list(csv.DictReader(io.StringIO(app.export_csv().decode("utf-8-sig"))))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["title"], "'=unsafe title")
            self.assertEqual(rows[1]["automatic_label"], "")
            self.assertEqual(rows[1]["human_label"], "B")
            self.assertEqual(rows[1]["needs_review"], "True")
            self.assertEqual(rows[1]["review_scope"], app.scope)

    def test_invalid_review_does_not_change_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = fixture(tmp)
            for args in [("train-id", "A", 0), ("a", "unknown-class", 0), ("a", "A", True), ("a", "A", -1)]:
                with self.assertRaises(ValueError):
                    app.review(*args)
            self.assertEqual(app.reviews.rows(), {})

    def test_cache_reuses_embeddings_and_rejects_tampering_or_different_input(self):
        class Encoder:
            identity = {"model": "test-only"}
            calls = 0

            def encode_documents(self, documents):
                self.calls += 1
                return Corpus(documents, [Chunk("a", 0, 0, 4, 4)], [[.3, .4]], self.identity)

        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "cache"
            encoder, docs = Encoder(), [Document("a", "text")]
            first, cached = cached_corpus(encoder, docs, directory)
            self.assertFalse(cached)
            second, cached = cached_corpus(encoder, docs, directory)
            self.assertTrue(cached)
            self.assertEqual(encoder.calls, 1)
            np.testing.assert_array_equal(first.vectors, second.vectors)
            with self.assertRaises(ValueError):
                cached_corpus(encoder, [Document("a", "changed")], directory)
            (directory / "index.json").write_text("{}")
            with self.assertRaisesRegex(ValueError, "checksum"):
                cached_corpus(encoder, docs, directory)


class BrowserHTTP(unittest.TestCase):
    def test_local_origin_token_routes_and_error_responses(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = fixture(tmp)
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(app, "test-token"))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            port = server.server_port

            def request(path, method="GET", body=None, headers=None):
                connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                try:
                    connection.request(method, path, body=body, headers=headers or {})
                    response = connection.getresponse()
                    return response.status, dict(response.getheaders()), response.read()
                finally:
                    connection.close()

            try:
                status, headers, body = request("/")
                self.assertEqual(status, 200)
                self.assertIn(b"ENINCA", body)
                self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
                self.assertEqual(request("/api/state", headers={"Host": "untrusted.example"})[0], 403)
                self.assertEqual(request("/api/state", headers={"Origin": "https://untrusted.example"})[0], 403)
                self.assertEqual(request("/../LICENSE")[0], 404)
                self.assertEqual(request("/api/document?id=missing")[0], 404)
                body = json.dumps(dict(document_id="a", label="B", revision=0))
                self.assertEqual(request("/api/review", "POST", body, {"Content-Type": "application/json"})[0], 403)
                valid = {"Content-Type": "application/json", "X-Demo-Token": "test-token"}
                self.assertEqual(request("/api/review", "POST", body, valid)[0], 200)
                self.assertEqual(request("/api/review", "POST", body, valid)[0], 409)
                self.assertEqual(request("/api/review", "POST", "[]", valid)[0], 400)
                self.assertEqual(request("/api/search", "POST", '{"query": null}', valid)[0], 400)
                self.assertEqual(request("/api/export.csv")[0], 200)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
