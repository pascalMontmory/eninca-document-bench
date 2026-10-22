"""Backend-independent document contracts and small-corpus retrieval tools."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

import numpy as np


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Document:
    id: str
    text: str
    label: str | None = None

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("Document id must be a nonempty string")
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError(f"Empty text for {self.id!r}; OCR/text extraction is required upstream")
        if self.label is not None and (not isinstance(self.label, str) or not self.label.strip()):
            raise ValueError("Label must be null or a nonempty string")


def validate_documents(documents):
    if not documents:
        raise ValueError("No documents")
    if len({d.id for d in documents}) != len(documents):
        raise ValueError("Duplicate document ids")


def read_jsonl(path: str | Path) -> list[Document]:
    documents = []
    with Path(path).open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                if not isinstance(record, dict) or set(record) - {"id", "text", "label"}:
                    raise ValueError("Expected id, text and optional label fields")
                documents.append(Document(**record))
            except (ValueError, TypeError) as exc:
                raise ValueError(f"{path}, line {number}: {exc}") from exc
    validate_documents(documents)
    return documents


def unit_rows(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float32)
    if values.ndim != 2 or not values.shape[0] or not values.shape[1] or not np.isfinite(values).all():
        raise ValueError("Expected a nonempty finite embedding matrix")
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    if (norms <= 1e-12).any():
        raise ValueError("Cannot normalize a zero embedding")
    return values / norms


@dataclass(frozen=True)
class Chunk:
    document_id: str
    ordinal: int
    start: int  # Unicode character offsets in the unmodified original text
    end: int
    tokens: int  # includes special tokens, excludes padding


class Corpus:
    """In-memory exact cosine search. Not a million-document vector database."""

    def __init__(self, documents, chunks, vectors, encoder_identity, timings=None):
        validate_documents(documents)
        self.documents = list(documents)
        self.chunks = list(chunks)
        self.vectors = unit_rows(vectors)
        if len(self.chunks) != len(self.vectors):
            raise ValueError("Chunk/vector count mismatch")
        self.encoder_identity = dict(encoder_identity)
        self.timings = dict(timings or {})
        self._documents = {d.id: d for d in self.documents}
        ordinals = {d.id: [] for d in self.documents}
        for chunk in self.chunks:
            if chunk.document_id not in self._documents:
                raise ValueError("Chunk references an unknown document")
            if not 0 <= chunk.start < chunk.end <= len(self._documents[chunk.document_id].text):
                raise ValueError("Invalid character span")
            if chunk.tokens <= 0:
                raise ValueError("Invalid token count")
            ordinals[chunk.document_id].append(chunk.ordinal)
        if any(values != list(range(len(values))) or not values for values in ordinals.values()):
            raise ValueError("Missing, duplicate or unordered chunks")

    def search(self, query_vector, *, encoder_identity, top_k=5):
        if encoder_identity != self.encoder_identity:
            raise ValueError("Query and index use different model/chunking contracts")
        if not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("top_k must be a positive integer")
        query = unit_rows(np.asarray(query_vector).reshape(1, -1))
        if query.shape[1] != self.vectors.shape[1]:
            raise ValueError("Query dimension mismatch")
        scores = self.vectors @ query[0]
        # Max chunk score per document; multiple chunks never crowd out other documents.
        best = {}
        for i, chunk in enumerate(self.chunks):
            current = best.get(chunk.document_id)
            if current is None or scores[i] > scores[current]:
                best[chunk.document_id] = i
        ordered = sorted(best.items(), key=lambda item: (-float(scores[item[1]]), item[0]))[:top_k]
        return [{"document_id": doc_id, "score": float(scores[i]),
                 "chunk": asdict(self.chunks[i]),
                 "excerpt": self._documents[doc_id].text[self.chunks[i].start:self.chunks[i].end]}
                for doc_id, i in ordered]

    def document_vectors(self):
        # Equal chunk mean, then normalization. Overlap is intentionally represented twice.
        lookup = {d.id: i for i, d in enumerate(self.documents)}
        means = np.zeros((len(self.documents), self.vectors.shape[1]), np.float32)
        counts = np.zeros(len(self.documents), np.int64)
        for vector, chunk in zip(self.vectors, self.chunks):
            i = lookup[chunk.document_id]
            means[i] += vector
            counts[i] += 1
        return unit_rows(means / counts[:, None])

    def save(self, directory: str | Path):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=False)
        vector_path = directory / "vectors.npy"
        np.save(vector_path, self.vectors, allow_pickle=False)
        record = {"schema": 1, "encoder": self.encoder_identity,
                  "documents": [asdict(d) | {"text_sha256": text_sha256(d.text)} for d in self.documents],
                  "chunks": [asdict(c) for c in self.chunks], "timings": self.timings,
                  "vectors_sha256": hashlib.sha256(vector_path.read_bytes()).hexdigest()}
        (directory / "index.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, directory: str | Path):
        directory = Path(directory)
        record = json.loads((directory / "index.json").read_text(encoding="utf-8"))
        if record.get("schema") != 1:
            raise ValueError("Unsupported index schema")
        vector_path = directory / "vectors.npy"
        if hashlib.sha256(vector_path.read_bytes()).hexdigest() != record["vectors_sha256"]:
            raise ValueError("Vector file checksum mismatch")
        documents = []
        for d in record["documents"]:
            if text_sha256(d["text"]) != d["text_sha256"]:
                raise ValueError("Document text checksum mismatch")
            documents.append(Document(d["id"], d["text"], d["label"]))
        return cls(documents, [Chunk(**c) for c in record["chunks"]],
                   np.load(vector_path, allow_pickle=False), record["encoder"], record["timings"])


class PrototypeClassifier:
    """Class centroids built ONLY from labeled training documents; no model fine-tuning."""

    def __init__(self, training: Corpus):
        labels = [d.label for d in training.documents]
        if any(label is None for label in labels) or len(set(labels)) < 2:
            raise ValueError("At least two labeled classes are required")
        self.labels = sorted(set(labels))
        vectors = training.document_vectors()
        self.centroids = unit_rows(np.stack([vectors[np.array(labels) == label].mean(axis=0)
                                             for label in self.labels]))
        self.encoder_identity = training.encoder_identity
        self.training_ids = {d.id for d in training.documents}
        self.training_hashes = {text_sha256(d.text) for d in training.documents}

    def predict(self, corpus: Corpus, *, min_score=0.4, min_margin=0.05):
        if not -1 <= min_score <= 1 or not 0 <= min_margin <= 2:
            raise ValueError("Invalid abstention thresholds")
        if corpus.encoder_identity != self.encoder_identity:
            raise ValueError("Training and evaluation use different encoders")
        if self.training_ids & {d.id for d in corpus.documents} or self.training_hashes & {text_sha256(d.text) for d in corpus.documents}:
            raise ValueError("Training/evaluation overlap (id or exact text)")
        scores = corpus.document_vectors() @ self.centroids.T
        output = []
        for document, row in zip(corpus.documents, scores):
            order = np.argsort(-row, kind="stable")
            first, second = order[:2]
            score, margin = float(row[first]), float(row[first] - row[second])
            accepted = score >= min_score and margin >= min_margin
            output.append({"document_id": document.id, "suggested_label": self.labels[first],
                           "label": self.labels[first] if accepted else None,
                           "needs_review": not accepted, "cosine_score": score, "margin": margin})
        return output


def classification_metrics(documents, predictions):
    if any(d.label is None for d in documents) or len(documents) != len(predictions):
        raise ValueError("Complete evaluation labels are required")
    if [d.id for d in documents] != [p["document_id"] for p in predictions]:
        raise ValueError("Prediction order mismatch")
    if not documents:
        raise ValueError("Empty evaluation")
    labels = sorted({d.label for d in documents} | {p["label"] for p in predictions if p["label"] is not None})
    pairs = [(d.label, p["label"]) for d, p in zip(documents, predictions)]
    accepted = sum(predicted is not None for _, predicted in pairs)
    correct = sum(truth == predicted for truth, predicted in pairs)
    f1 = []
    for label in labels:
        tp = sum(a == b == label for a, b in pairs)
        fp = sum(a != label and b == label for a, b in pairs)
        fn = sum(a == label and b != label for a, b in pairs)
        f1.append(2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.)
    return {"documents": len(documents), "coverage": accepted / len(documents),
            "accuracy_with_abstentions_as_errors": correct / len(documents),
            "accuracy_accepted": correct / accepted if accepted else None,
            "macro_f1_with_abstentions_as_errors": float(np.mean(f1))}
