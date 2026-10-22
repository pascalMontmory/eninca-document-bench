"""Local public-corpus workflow. Human decisions never train the classifier."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import time

import numpy as np

from eninca_documents.calibration import calibrate, decision_metrics, predict_calibrated
from eninca_documents.core import Corpus, PrototypeClassifier, read_jsonl
from eninca_documents.encoder import OnnxEncoder

ROOT = Path(__file__).resolve().parents[1]
OUTSIDE = "out_of_scope"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode("utf-8")


class Conflict(ValueError):
    pass


class Reviews:
    """Append-only local decisions; optimistic revisions prevent stale-tab overwrites."""

    def __init__(self, path, scope):
        self.path, self.scope = path, scope
        with sqlite3.connect(path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS reviews (scope TEXT, document_id TEXT, "
                       "revision INTEGER, label TEXT, saved_utc TEXT, "
                       "PRIMARY KEY(scope, document_id, revision))")

    def rows(self):
        with sqlite3.connect(self.path) as db:
            rows = db.execute("SELECT document_id, revision, label, saved_utc FROM reviews "
                              "WHERE scope=? ORDER BY revision", (self.scope,)).fetchall()
        return {doc: dict(revision=rev, label=label, saved_utc=stamp) for doc, rev, label, stamp in rows}

    def save(self, document_id, label, revision):
        with sqlite3.connect(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            last = db.execute("SELECT MAX(revision) FROM reviews WHERE scope=? AND document_id=?",
                              (self.scope, document_id)).fetchone()[0] or 0
            if last != revision:
                raise Conflict("stale_review")
            stamp = datetime.now(timezone.utc).isoformat()
            db.execute("INSERT INTO reviews VALUES (?, ?, ?, ?, ?)",
                       (self.scope, document_id, last + 1, label, stamp))
        return dict(revision=last + 1, label=label, saved_utc=stamp)


def cached_corpus(encoder, documents, directory):
    if not directory.exists():
        corpus = encoder.encode_documents(documents)
        directory.parent.mkdir(parents=True, exist_ok=True)
        # Publish a complete index atomically, never a partially written directory.
        with tempfile.TemporaryDirectory(prefix="index-", dir=directory.parent) as temporary:
            stage = Path(temporary) / "complete"
            corpus.save(stage)
            (stage / "index.sha256").write_text(digest((stage / "index.json").read_bytes()), encoding="ascii")
            stage.rename(directory)
        cached = False
    else:
        cached = True
    # Use the same load/normalization path on first launch and subsequent launches.
    if (directory / "index.sha256").read_text(encoding="ascii") != digest((directory / "index.json").read_bytes()):
        raise ValueError("Index checksum mismatch")
    corpus = Corpus.load(directory)
    if corpus.encoder_identity != encoder.identity or corpus.documents != documents:
        raise ValueError("Cache/model/corpus mismatch")
    return corpus, cached


class Demo:
    def __init__(self, model_dir, state_dir):
        self.model_dir, self.state_dir = Path(model_dir), Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.status_lock = threading.Lock()
        self.phase, self.ready, self.error = "starting", False, False
        self.started = time.perf_counter()

    def progress(self, phase):
        with self.status_lock:
            self.phase = phase
        print(f"Demo: {phase}", flush=True)

    def status(self):
        with self.status_lock:
            return dict(phase=self.phase, ready=self.ready, error=self.error,
                        elapsed_seconds=time.perf_counter() - self.started)

    def prepare(self):
        self.progress("checking_corpus")
        # The launcher runs the full XML/split verifier. Also enforce pinned file
        # hashes here for callers starting the Python module directly.
        data_dir = ROOT / "data/dila-v1"
        manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
        for name, expected in manifest["files"].items():
            if digest((data_dir / name).read_bytes()) != expected:
                raise ValueError("Corpus checksum mismatch")
        self.metadata = {row["id"]: row for row in manifest["documents"]}
        self.progress("loading_model")
        self.encoder = OnnxEncoder(self.model_dir, batch_size=4, threads=2, sort_by_length=True)
        contract = dict(schema=1, encoder=self.encoder.identity,
                        data=digest((data_dir / "manifest.json").read_bytes()),
                        source={p.name: digest(p.read_bytes()) for p in sorted((ROOT / "src/eninca_documents").glob("*.py"))},
                        versions={name: importlib.metadata.version(name) for name in ("numpy", "onnxruntime", "tokenizers")})
        self.cache_key = digest(json_bytes(contract))
        corpus, self.cache_hits = {}, {}
        for split in ("train", "validation", "test"):
            self.progress("indexing_" + split)
            corpus[split], self.cache_hits[split] = cached_corpus(
                self.encoder, read_jsonl(data_dir / (split + ".jsonl")),
                self.state_dir / "indexes" / self.cache_key / split)
        self.progress("calibrating")
        classifier = PrototypeClassifier(corpus["train"])
        self.labels = classifier.labels
        self.policy = calibrate(classifier, corpus["validation"])
        predictions = predict_calibrated(classifier, corpus["test"], self.policy)
        self.predictions = {p["document_id"]: p for p in predictions}
        self.metrics = decision_metrics(corpus["test"].documents, predictions, self.labels)
        self.search_corpus = Corpus(
            [d for c in corpus.values() for d in c.documents],
            [chunk for c in corpus.values() for chunk in c.chunks],
            np.concatenate([c.vectors for c in corpus.values()]), self.encoder.identity)
        self.documents = {d.id: d for d in self.search_corpus.documents}
        # A changed model, calibration or predictions starts an independent review
        # scope; old decisions remain in SQLite, never silently migrate.
        self.scope = digest(json_bytes(dict(cache=self.cache_key, policy=self.policy, predictions=predictions)))
        self.reviews = Reviews(self.state_dir / "reviews.sqlite3", self.scope)
        self.encoding_times = {s: c.timings["encode_seconds"] for s, c in corpus.items()}
        self.preparation_seconds = time.perf_counter() - self.started
        self.search_count, self.search_seconds = 0, 0.
        self.progress("ready")
        with self.status_lock:
            self.ready = True

    def snapshot(self):
        with self.lock:
            reviews = self.reviews.rows()
            rows = []
            for doc_id, prediction in self.predictions.items():
                meta = self.metadata[doc_id]
                rows.append(dict(prediction, title=meta["title"],
                                 review=reviews.get(doc_id, dict(revision=0, label=None, saved_utc=None))))
            reviewed = [r for r in rows if r["review"]["label"] is not None]
            return dict(documents=len(self.documents), chunks=len(self.search_corpus.chunks),
                        labels=self.labels, rows=rows, metrics=self.metrics,
                        policy={k: self.policy[k] for k in ("mode", "min_score", "min_margin")},
                        timings=dict(preparation_seconds=self.preparation_seconds,
                                     original_encoding_seconds=self.encoding_times, cache_hits=self.cache_hits,
                                     search_count=self.search_count, search_seconds=self.search_seconds),
                        review_counts=dict(completed=len(reviewed), remaining=len(rows)-len(reviewed),
                                           changed_suggestion=sum(r["review"]["label"] != r["suggested_label"] for r in reviewed),
                                           outside=sum(r["review"]["label"] == OUTSIDE for r in reviewed)),
                        scope=self.scope)

    def document(self, doc_id):
        doc = self.documents[doc_id]
        meta = self.metadata[doc_id]
        return dict(id=doc_id, title=meta["title"], text=doc.text,
                    source_url=meta["source_url"], source_modified=meta["source_modified"])

    def search(self, query):
        if not isinstance(query, str) or not query.strip() or len(query) > 2000:
            raise ValueError("invalid_query")
        with self.lock:  # Tokenizer/session are shared; keep inference serialized.
            start = time.perf_counter()
            try:
                vector = self.encoder.encode_query(query)
            except ValueError as exc:
                raise ValueError("query_too_long_or_empty") from exc
            results = self.search_corpus.search(vector, encoder_identity=self.encoder.identity, top_k=5)
            elapsed = time.perf_counter() - start
            self.search_count += 1
            self.search_seconds += elapsed
            return dict(seconds=elapsed, results=[dict(r, title=self.metadata[r["document_id"]]["title"]) for r in results])

    def review(self, doc_id, label, revision):
        if not isinstance(doc_id, str) or doc_id not in self.predictions:
            raise ValueError("invalid_document")
        if label is not None and label not in [*self.labels, OUTSIDE]:
            raise ValueError("invalid_label")
        if type(revision) is not int or revision < 0:
            raise ValueError("invalid_revision")
        with self.lock:
            return self.reviews.save(doc_id, label, revision)

    def export_csv(self):
        output = io.StringIO(newline="")
        writer = csv.writer(output)
        writer.writerow(["document_id", "title", "suggested_label", "automatic_label", "needs_review",
                         "cosine_score", "margin", "human_label", "revision", "saved_utc", "review_scope"])
        for row in self.snapshot()["rows"]:
            cells = [row["document_id"], row["title"], row["suggested_label"], row["label"],
                     row["needs_review"], row["cosine_score"], row["margin"], row["review"]["label"],
                     row["review"]["revision"], row["review"]["saved_utc"], self.scope]
            # Protect spreadsheet consumers, including formulas after leading whitespace.
            writer.writerow(["'" + c if isinstance(c, str) and c.lstrip().startswith(("=", "+", "-", "@")) else c for c in cells])
        return ("\ufeff" + output.getvalue()).encode("utf-8")
