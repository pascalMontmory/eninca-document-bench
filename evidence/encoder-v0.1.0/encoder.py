"""A measured CPU reference, not a TPU encoder. Pooling follows the model card."""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

from .core import Chunk, Corpus, Document, unit_rows, validate_documents
from .model import verify_model


def mean_pool(hidden, mask):
    if hidden.ndim != 3 or hidden.shape[:2] != mask.shape or not np.isfinite(hidden).all():
        raise ValueError("Invalid transformer output")
    weights = mask.astype(np.float32)[..., None]
    counts = weights.sum(axis=1)
    if (counts == 0).any():
        raise ValueError("Empty attention mask")
    return (hidden.astype(np.float32) * weights).sum(axis=1) / counts


class OnnxEncoder:
    def __init__(self, model_directory, *, batch_size=8, threads=2, stride=16, sort_by_length=True):
        if batch_size < 1 or threads < 1 or not 0 <= stride < 126:
            raise ValueError("Invalid batch size, threads or stride")
        start = time.perf_counter()
        lock = verify_model(model_directory)
        directory = Path(model_directory)
        self.tokenizer = Tokenizer.from_file(str(directory / "tokenizer.json"))
        self.tokenizer.no_padding()
        self.tokenizer.enable_truncation(max_length=128, stride=stride)
        self.pad_id = self.tokenizer.token_to_id("<pad>")
        if self.pad_id is None or self.tokenizer.num_special_tokens_to_add(False) != 2:
            raise ValueError("Unexpected tokenizer contract")
        options = ort.SessionOptions()
        options.intra_op_num_threads = threads
        options.inter_op_num_threads = 1
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        self.session = ort.InferenceSession(str(directory / "onnx/model.onnx"), options,
                                            providers=["CPUExecutionProvider"])
        self.input_names = {entry.name for entry in self.session.get_inputs()}
        if self.input_names != {"input_ids", "attention_mask", "token_type_ids"}:
            raise ValueError(f"Unexpected ONNX inputs: {self.input_names}")
        self.output_name = self.session.get_outputs()[0].name
        self.identity = {"model_id": lock["model_id"], "revision": lock["revision"],
                         "onnx_sha256": lock["files"]["onnx/model.onnx"]["sha256"],
                         "tokenizer_sha256": lock["files"]["tokenizer.json"]["sha256"],
                         "max_tokens": 128, "stride": stride,
                         "pooling": "attention-mask-mean-then-l2", "dimension": 384}
        self.batch_size, self.threads = batch_size, threads
        self.sort_by_length = sort_by_length
        self.setup_seconds = time.perf_counter() - start

    def chunks(self, documents):
        validate_documents(documents)
        metadata, encodings = [], []
        for document in documents:
            encoding = self.tokenizer.encode(document.text)
            # Include every overflowing window. No silently discarded document tail.
            for ordinal, part in enumerate([encoding, *encoding.overflowing]):
                offsets = [offset for offset, special in zip(part.offsets, part.special_tokens_mask)
                           if not special and offset[1] > offset[0]]
                if not offsets:
                    raise ValueError(f"Document {document.id!r} contains no usable tokens")
                metadata.append(Chunk(document.id, ordinal, min(a for a, _ in offsets),
                                      max(b for _, b in offsets), len(part.ids)))
                encodings.append(part)
        return metadata, encodings

    def encode_documents(self, documents):
        started = time.perf_counter()
        chunks, encoded = self.chunks(documents)
        tokenization_seconds = time.perf_counter() - started
        order = list(range(len(encoded)))
        if self.sort_by_length:
            order.sort(key=lambda i: len(encoded[i].ids))
        vectors = np.empty((len(encoded), 384), np.float32)
        inference_seconds = pooling_seconds = 0.
        padded = 0
        for begin in range(0, len(order), self.batch_size):
            indices = order[begin:begin + self.batch_size]
            length = max(len(encoded[i].ids) for i in indices)
            ids = np.full((len(indices), length), self.pad_id, np.int64)
            mask = np.zeros_like(ids)
            types = np.zeros_like(ids)
            for row, index in enumerate(indices):
                part = encoded[index]
                ids[row, :len(part.ids)] = part.ids
                mask[row, :len(part.ids)] = part.attention_mask
                types[row, :len(part.ids)] = part.type_ids
            padded += ids.size
            before = time.perf_counter()
            hidden = self.session.run([self.output_name], {"input_ids": ids,
                                      "attention_mask": mask, "token_type_ids": types})[0]
            inference_seconds += time.perf_counter() - before
            before = time.perf_counter()
            pooled = unit_rows(mean_pool(hidden, mask))
            if pooled.shape != (len(indices), 384):
                raise ValueError("Unexpected embedding dimensions")
            vectors[indices] = pooled  # restore input/document/chunk order after length grouping
            pooling_seconds += time.perf_counter() - before
        timings = {"tokenization_seconds": tokenization_seconds, "inference_seconds": inference_seconds,
                   "pooling_seconds": pooling_seconds, "tokens": sum(c.tokens for c in chunks),
                   "padded_tokens": padded, "chunks": len(chunks), "documents": len(documents),
                   "batch_size": self.batch_size, "threads": self.threads,
                   "sort_by_length": self.sort_by_length}
        result = Corpus(documents, chunks, vectors, self.identity, timings)
        result.timings["encode_seconds"] = time.perf_counter() - started
        return result

    def encode_query(self, text):
        document = Document("query", text)
        chunks, _ = self.chunks([document])
        if len(chunks) != 1:
            raise ValueError("Query exceeds 126 content tokens; shorten the query")
        return self.encode_documents([document]).vectors[0]
