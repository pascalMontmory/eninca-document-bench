"""Local CLI; only fetch-model accesses the network."""
import argparse
import datetime
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import statistics
import time

import numpy as np

from .core import Corpus, PrototypeClassifier, classification_metrics, read_jsonl
from .encoder import OnnxEncoder
from .model import fetch_model, file_sha256


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def provenance():
    cpu_model = platform.processor() or None
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.is_file():
        cpu_model = next((line.split(":", 1)[1].strip() for line in cpuinfo.read_text().splitlines()
                          if line.startswith("model name")), cpu_model)
    return {"created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "platform": platform.system(), "machine": platform.machine(),
            "cpu_model": cpu_model, "logical_cpus": os.cpu_count(),
            "python": platform.python_version(),
            "packages": {name: importlib.metadata.version(name)
                         for name in ("numpy", "onnxruntime", "tokenizers")},
            "source_sha256": {p.name: file_sha256(p) for p in sorted(Path(__file__).parent.iterdir())
                              if p.suffix in (".py", ".json")}}


def evaluate_retrieval(corpus, encoder, queries):
    if not queries:
        raise ValueError("No evaluation queries")
    known = {d.id for d in corpus.documents}
    rows = []
    for query in queries:
        relevant = set(query["relevant_ids"])
        if not relevant or not relevant <= known:
            raise ValueError("Unknown or missing retrieval relevance labels")
        hits = corpus.search(encoder.encode_query(query["text"]), encoder_identity=encoder.identity, top_k=3)
        ids = [hit["document_id"] for hit in hits]
        rank = next((i + 1 for i, doc_id in enumerate(ids) if doc_id in relevant), None)
        rows.append({"id": query["id"], "retrieved_ids": ids, "relevant_ids": sorted(relevant),
                     "recall_at_3": len(set(ids) & relevant) / len(relevant),
                     "reciprocal_rank_at_3": 1 / rank if rank else 0.,
                     "top1_correct": ids[0] in relevant})
    return {"queries": len(rows), "top1_accuracy": float(np.mean([r["top1_correct"] for r in rows])),
            "mean_recall_at_3": float(np.mean([r["recall_at_3"] for r in rows])),
            "mrr_at_3": float(np.mean([r["reciprocal_rank_at_3"] for r in rows])), "details": rows}


def run_demo(args, encoder):
    out, data = Path(args.out), Path(args.data_dir)
    out.mkdir(parents=True, exist_ok=False)
    documents = read_jsonl(data / "documents.jsonl")
    training = read_jsonl(data / "training.jsonl")
    evaluation = read_jsonl(data / "evaluation.jsonl")
    queries = json.loads((data / "queries.json").read_text(encoding="utf-8"))
    if args.repetitions < 1:
        raise ValueError("repetitions must be positive")
    # Warm both shape schedules before timing. All encoder runs are synchronous CPU calls.
    warm = {}
    for ordered in (False, True):
        encoder.sort_by_length = ordered
        warm[ordered] = encoder.encode_documents(documents)
    reference = warm[False]
    np.testing.assert_allclose(reference.vectors, warm[True].vectors, atol=3e-5, rtol=3e-5)
    raw, errors = [], []
    for repetition in range(args.repetitions):
        schedules = (False, True) if repetition % 2 == 0 else (True, False)
        for sorted_batches in schedules:
            encoder.sort_by_length = sorted_batches
            result = encoder.encode_documents(documents)
            if result.chunks != reference.chunks:
                raise AssertionError("Reordered or missing chunks")
            error = float(np.max(np.abs(result.vectors - reference.vectors)))
            errors.append(error)
            np.testing.assert_allclose(reference.vectors, result.vectors, atol=3e-5, rtol=3e-5)
            raw.append({"repetition": repetition + 1, **result.timings})
        print(f"CPU repetition {repetition + 1}/{args.repetitions}: chunk order and embeddings PASS", flush=True)
    encoder.sort_by_length = True
    retrieval = evaluate_retrieval(warm[True], encoder, queries)
    classifier = PrototypeClassifier(encoder.encode_documents(training))
    predicted = classifier.predict(encoder.encode_documents(evaluation),
                                   min_score=args.min_score, min_margin=args.min_margin)
    quality = classification_metrics(evaluation, predicted)
    export_start = time.perf_counter()
    warm[True].save(out / "index")
    export_seconds = time.perf_counter() - export_start
    # A fresh read and actual export give a separately reported complete local indexing time.
    e2e_start = time.perf_counter()
    full = encoder.encode_documents(read_jsonl(data / "documents.jsonl"))
    full.save(out / "index-end-to-end")
    e2e_seconds = time.perf_counter() - e2e_start
    summary = {}
    for sorted_batches in (False, True):
        runs = [r for r in raw if r["sort_by_length"] == sorted_batches]
        seconds = statistics.median(r["encode_seconds"] for r in runs)
        summary["length_grouped" if sorted_batches else "input_order"] = {
            "median_encode_seconds": seconds, "documents_per_second": len(documents) / seconds,
            "padding_fraction": 1 - runs[0]["tokens"] / runs[0]["padded_tokens"]}
    report = {"status": "pass", "scope": "CPU prototype on authored synthetic French documents; not an industrial benchmark",
              "backend": "ONNX Runtime CPUExecutionProvider", "tpu_tested": False,
              "encoder": encoder.identity, "environment": provenance(),
              "data_sha256": {p.name: file_sha256(p) for p in sorted(data.iterdir()) if p.suffix in (".json", ".jsonl")},
              "setup_seconds_including_hash_checks": encoder.setup_seconds,
              "index_export_seconds": export_seconds,
              "end_to_end_index_seconds_excluding_model_setup": e2e_seconds,
              "indexing_scope": "JSONL read, tokenization, all chunks, inference, pooling, validation, index export",
              "timing_repetitions_are_not_independent_quality_samples": True,
              "documents": len(documents), "chunks": len(reference.chunks),
              "max_abs_embedding_difference_between_batch_orders": max(errors),
              "timings": raw, "summary": summary, "retrieval": retrieval,
              "classification": quality, "predictions": predicted,
              "abstention_thresholds": {"min_score": args.min_score, "min_margin": args.min_margin},
              "thresholds_calibrated": False}
    write_json(out / "report.json", report)
    print(json.dumps({"retrieval": {k: v for k, v in retrieval.items() if k != "details"},
                      "classification": quality, "report": str(out / "report.json")}, ensure_ascii=False, indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(description="ENINCA local documentary prototype (CPU)")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("fetch-model", "index", "search", "classify", "demo"):
        command = sub.add_parser(name)
        command.add_argument("--model-dir", required=True)
        if name == "fetch-model":
            continue
        command.add_argument("--batch-size", type=int, default=8)
        command.add_argument("--threads", type=int, default=2)
        if name in ("index", "classify"):
            command.add_argument("--input", required=True, help="UTF-8 JSONL (id, text, optional label)")
        if name in ("index", "classify", "demo"):
            command.add_argument("--out", required=True, help="New output path; never overwrites")
        if name == "search":
            command.add_argument("--index", required=True)
            command.add_argument("--query", required=True)
            command.add_argument("--top-k", type=int, default=5)
        if name in ("classify", "demo"):
            command.add_argument("--min-score", type=float, default=.4)
            command.add_argument("--min-margin", type=float, default=.05)
        if name == "classify":
            command.add_argument("--training", required=True, help="Separate labeled JSONL")
        if name == "demo":
            command.add_argument("--data-dir", required=True)
            command.add_argument("--repetitions", type=int, default=3)
    args = parser.parse_args(argv)
    if args.command == "fetch-model":
        fetch_model(args.model_dir)
        print("Pinned model files: PASS")
        return
    encoder = OnnxEncoder(args.model_dir, batch_size=args.batch_size, threads=args.threads)
    if args.command == "demo":
        run_demo(args, encoder)
    elif args.command == "index":
        started = time.perf_counter()
        corpus = encoder.encode_documents(read_jsonl(args.input))
        corpus.save(args.out)
        write_json(Path(args.out) / "run.json", {"environment": provenance(), "encoder": encoder.identity,
                   "setup_seconds": encoder.setup_seconds, "timings": corpus.timings,
                   "index_seconds_including_input_and_export": time.perf_counter() - started,
                   "input_sha256": file_sha256(args.input)})
        print(f"Indexed {len(corpus.documents)} documents / {len(corpus.chunks)} chunks in {args.out}")
    elif args.command == "search":
        corpus = Corpus.load(args.index)
        result = corpus.search(encoder.encode_query(args.query), encoder_identity=encoder.identity, top_k=args.top_k)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "classify":
        training = encoder.encode_documents(read_jsonl(args.training))
        evaluation = encoder.encode_documents(read_jsonl(args.input))
        predictions = PrototypeClassifier(training).predict(evaluation, min_score=args.min_score, min_margin=args.min_margin)
        write_json(args.out, {"environment": provenance(), "encoder": encoder.identity,
                   "training_input_sha256": file_sha256(args.training), "input_sha256": file_sha256(args.input),
                   "thresholds": {"min_score": args.min_score, "min_margin": args.min_margin},
                   "thresholds_calibrated": False, "predictions": predictions})
        print(f"Wrote {len(predictions)} assisted classifications to {args.out}")


if __name__ == "__main__":
    main()
