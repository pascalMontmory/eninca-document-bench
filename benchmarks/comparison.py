"""Fixed paired CPU comparison: complete warm indexing, not a competitor benchmark."""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import statistics
import sys
import tempfile
import time

import numpy as np

from eninca_documents.calibration import calibrate, decision_metrics, predict_calibrated
from eninca_documents.cli import provenance, write_json
from eninca_documents.core import PrototypeClassifier, read_jsonl
from eninca_documents.encoder import OnnxEncoder

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ("reference", "length_grouped")
ATOL = RTOL = 3e-5


class Cancelled(Exception):
    pass


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def paired_summary(rows):
    pairs = {}
    for row in rows:
        pair, variant = int(row["pair"]), row["variant"]
        if variant not in VARIANTS or variant in pairs.setdefault(pair, {}):
            raise ValueError("Unknown or duplicate variant")
        seconds = float(row["index_seconds"])
        if not math.isfinite(seconds) or seconds <= 0:
            raise ValueError("Invalid timing")
        pairs[pair][variant] = seconds
    if len(pairs) < 3 or any(set(p) != set(VARIANTS) for p in pairs.values()):
        raise ValueError("At least three complete pairs are required")
    if sorted(pairs) != list(range(1, len(pairs) + 1)):
        raise ValueError("Noncontiguous pair numbers")
    ratios = np.array([p["reference"] / p["length_grouped"] for _, p in sorted(pairs.items())])
    # Resample whole paired ratios, never treat the two arms as independent runs.
    rng = np.random.default_rng(20261022)
    boot = np.median(ratios[rng.integers(0, len(ratios), size=(10000, len(ratios)))], axis=1)
    low, high = (float(x) for x in np.quantile(boot, [.025, .975]))
    ratio = float(np.median(ratios))
    verdict = "observed_gain" if low > 1 else "observed_regression" if high < 1 else "inconclusive"
    return dict(pairs=len(pairs), median_paired_speedup=ratio,
                median_paired_time_reduction_pct=float(np.median(100 * (1 - 1 / ratios))),
                paired_speedup_bootstrap95=[low, high], faster_pairs=int((ratios > 1).sum()),
                verdict=verdict,
                uncertainty="Descriptive paired percentile bootstrap, 10000 resamples. Few repeated timings on identical documents; shared-host drift and workload generalization are not covered.")


def check_outputs(reference, current):
    if reference.documents != current.documents or reference.chunks != current.chunks or reference.encoder_identity != current.encoder_identity:
        raise AssertionError("Document, chunk or encoder contract changed")
    np.testing.assert_allclose(current.vectors, reference.vectors, atol=ATOL, rtol=RTOL)
    return float(np.max(np.abs(current.vectors - reference.vectors)))


def run_comparison(encoder, output, *, progress=lambda _: None, cancelled=lambda: False,
                   input_path=None, repetitions=7, count=48):
    if not 3 <= repetitions <= 31 or count < 6:
        raise ValueError("Use 3..31 pairs and at least six documents")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    old = encoder.batch_size, encoder.sort_by_length
    started = time.perf_counter()
    total, done = 2 * repetitions + (6 if input_path is None else 2), 0

    def notify(phase, *, advance=False, **detail):
        nonlocal done
        if advance:
            done += 1
        progress(dict(phase=phase, completed=done, total=total, elapsed_seconds=time.perf_counter()-started, **detail))
        if cancelled():
            raise Cancelled("Cancelled between inference passes")

    try:
        notify("checking_data")
        data = ROOT / "data/dila-v1"
        if input_path is None:
            manifest = json.loads((data / "manifest.json").read_text())
            for name, expected in manifest["files"].items():
                if sha(data / name) != expected:
                    raise ValueError("Public corpus checksum mismatch")
            sets = {s: read_jsonl(data / (s + ".jsonl")) for s in ("train", "validation", "test")}
            candidates = sets["train"] + sets["validation"]
            data_hash = sha(data / "manifest.json")
        else:
            candidates = read_jsonl(input_path)
            data_hash = sha(input_path)
        if count > len(candidates):
            raise ValueError("Requested sample exceeds available documents")
        candidates.sort(key=lambda d: (len(d.text), d.id))
        selected = [candidates[i] for i in np.linspace(0, len(candidates)-1, count, dtype=int)]
        # Deterministic shuffle avoids handing the reference an already sorted workload.
        order_rng = np.random.default_rng(20261023)
        selected = [selected[i] for i in order_rng.permutation(count)]
        orders = [list(VARIANTS if i % 2 == 0 else reversed(VARIANTS)) for i in range(repetitions)]
        order_rng.shuffle(orders)
        source_paths = [Path(__file__), *sorted((ROOT / "src/eninca_documents").glob("*.py")),
                        ROOT / "src/eninca_documents/model.lock.json"]
        plan = dict(schema=1, created_utc=datetime.now(timezone.utc).isoformat(),
                    input_kind="public_dila" if input_path is None else "local_jsonl",
                    input_sha256=data_hash, timing_document_ids=[d.id for d in selected],
                    selected_texts_sha256=hashlib.sha256(json.dumps([asdict(d) for d in selected], ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
                    configurations={v: dict(batch_size=4, sort_by_length=v == "length_grouped", threads=encoder.threads) for v in VARIANTS},
                    pair_orders=orders, atol=ATOL, rtol=RTOL,
                    source_sha256={str(p.relative_to(ROOT)): sha(p) for p in source_paths})
        write_json(output / "plan.json", plan)  # Fixed before all quality and timing observations.
        encoder.batch_size, encoder.sort_by_length = 4, False
        quality = dict(status="not_evaluated", reason="No held-out business labels or relevance judgments provided")
        if input_path is None:
            notify("quality_train")
            training = encoder.encode_documents(sets["train"])
            notify("quality_validation", advance=True)
            validation = encoder.encode_documents(sets["validation"])
            classifier = PrototypeClassifier(training)
            policy = calibrate(classifier, validation)
            write_json(output / "calibration.json", policy)
            del training, validation
            notify("quality_reference", advance=True)
            ref_test = encoder.encode_documents(sets["test"])
            ref_pred = predict_calibrated(classifier, ref_test, policy)
            notify("quality_optimized", advance=True)
            encoder.sort_by_length = True
            opt_test = encoder.encode_documents(sets["test"])
            difference = check_outputs(ref_test, opt_test)
            opt_pred = predict_calibrated(classifier, opt_test, policy)
            fields = ("document_id", "suggested_label", "label", "needs_review")
            matching = sum(all(a[k] == b[k] for k in fields) for a, b in zip(ref_pred, opt_pred))
            if matching != len(ref_pred):
                raise AssertionError("Held-out classification decisions changed")
            quality = dict(status="pass", documents=len(ref_pred), matching_decisions=matching,
                           max_abs_embedding_difference=difference,
                           reference=decision_metrics(sets["test"], ref_pred, classifier.labels),
                           optimized=decision_metrics(sets["test"], opt_pred, classifier.labels),
                           retrieval_quality="not_evaluated: no independent public relevance judgments",
                           human_review_time="not_measured")
            write_json(output / "predictions.json", dict(reference=ref_pred, optimized=opt_pred))
            notify("quality_pass", advance=True)
            del ref_test, opt_test
        rows, reference = [], None
        with tempfile.TemporaryDirectory(prefix="working-", dir=output) as temporary:
            work = Path(temporary)
            selected_path = work / "input.jsonl"
            selected_path.write_text("".join(json.dumps(asdict(d), ensure_ascii=False) + "\n" for d in selected), encoding="utf-8")

            def execute(variant):
                encoder.sort_by_length = variant == "length_grouped"
                with tempfile.TemporaryDirectory(prefix="output-", dir=work) as dest:
                    before = time.perf_counter()
                    current = encoder.encode_documents(read_jsonl(selected_path))
                    after_encoding = time.perf_counter()
                    current.save(Path(dest) / "index")
                    finished = time.perf_counter()
                    seconds = finished - before
                    export_seconds = finished - after_encoding
                    return current, seconds, export_seconds

            for variant in VARIANTS:
                notify("warmup", variant=variant)
                current, _, _ = execute(variant)
                if reference is None:
                    reference = current
                check_outputs(reference, current)
                notify("warmup_done", advance=True, variant=variant)
            for pair, order in enumerate(orders, 1):
                for position, variant in enumerate(order, 1):
                    notify("measurement", pair=pair, pairs=repetitions, variant=variant)
                    load = list(os.getloadavg()) if hasattr(os, "getloadavg") else None
                    current, seconds, export_seconds = execute(variant)
                    difference = check_outputs(reference, current)
                    row = dict(pair=pair, position=position, variant=variant, index_seconds=seconds,
                               encode_seconds=current.timings["encode_seconds"], export_seconds=export_seconds,
                               documents=len(current.documents), chunks=len(current.chunks),
                               tokens=current.timings["tokens"], padded_tokens=current.timings["padded_tokens"],
                               max_abs_embedding_difference=difference,
                               load_average_1m=load[0] if load else None)
                    rows.append(row)
                    with (output / "timings.csv").open("w", newline="") as stream:
                        writer = csv.DictWriter(stream, fieldnames=list(row))
                        writer.writeheader(); writer.writerows(rows)
                    notify("measurement_done", advance=True, pair=pair, pairs=repetitions, variant=variant)
        variants = {}
        for variant in VARIANTS:
            selected_rows = [r for r in rows if r["variant"] == variant]
            times = [r["index_seconds"] for r in selected_rows]
            seconds = statistics.median(times)
            variants[variant] = dict(median_index_seconds=seconds, min_index_seconds=min(times), max_index_seconds=max(times),
                                     median_encode_seconds=statistics.median(r["encode_seconds"] for r in selected_rows),
                                     median_export_seconds=statistics.median(r["export_seconds"] for r in selected_rows),
                                     documents_per_second=count/seconds, chunks_per_second=len(reference.chunks)/seconds,
                                     padding_fraction=1-selected_rows[0]["tokens"]/selected_rows[0]["padded_tokens"])
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        report = dict(schema=1, status="pass", plan=plan, backend="ONNX Runtime CPUExecutionProvider", tpu_tested=False,
                      environment=provenance(), encoder=encoder.identity,
                      documents=count, chunks=len(reference.chunks), repetitions=repetitions,
                      variants=variants, comparison=paired_summary(rows), quality=quality,
                      peak_process_rss_bytes=rss if sys.platform == "darwin" else rss*1024,
                      campaign_seconds=time.perf_counter()-started,
                      outputs_sha256={p.name:sha(p) for p in output.iterdir() if p.is_file()},
                      timing_scope="Warm synchronous complete local indexing: JSONL read, tokenization, all chunks, CPU inference, pooling, validation and buffered index export. Model setup, warmups, quality evaluation, output comparisons and temporary-directory cleanup excluded. No fsync or remote storage.",
                      memory_scope="Cumulative process peak including initialization, quality/reference arrays and any pre-existing demo state; not memory per variant.",
                      limitations=["Both arms use the same existing MiniLM model and ENINCA encoder; reference is not a customer or commercial product.",
                                   "Only length grouping changes. Fixed batch size four, no parameter search in this campaign.",
                                   "Timing documents and model have been used in earlier experiments; new measurements are not unseen workload validation.",
                                   "Repeated timings on a shared machine do not establish industrial throughput or cost savings.",
                                   "No OCR, accelerator, business retrieval quality or human-review-time gain established."])
        write_json(output / "report.json", report)
        notify("complete")
        return report
    except Exception as exc:
        write_json(output / "failure.json", dict(status="cancelled" if isinstance(exc, Cancelled) else "fail", error=str(exc)))
        raise
    finally:
        encoder.batch_size, encoder.sort_by_length = old


def verify_report(directory):
    directory = Path(directory)
    report = json.loads((directory / "report.json").read_text())
    if report.get("status") != "pass" or report.get("schema") != 1:
        raise ValueError("Incomplete comparison")
    for name, expected in report["outputs_sha256"].items():
        if Path(name).name != name or sha(directory / name) != expected:
            raise ValueError("Comparison output checksum mismatch")
    with (directory / "timings.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    if paired_summary(rows) != report["comparison"]:
        raise ValueError("Summary does not match raw pairs")
    for variant in VARIANTS:
        values = [float(r["index_seconds"]) for r in rows if r["variant"] == variant]
        if len(values) != report["repetitions"] or statistics.median(values) != report["variants"][variant]["median_index_seconds"]:
            raise ValueError("Variant timings mismatch")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir")
    parser.add_argument("--out")
    parser.add_argument("--input", help="Optional authorized local JSONL; no business quality claim without labels/protocol")
    parser.add_argument("--repetitions", type=int, default=7)
    parser.add_argument("--documents", type=int, default=48)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--verify", help="Verify an existing report and its raw CSV without inference")
    args = parser.parse_args()
    if args.verify:
        report = verify_report(args.verify)
        print(json.dumps(report["comparison"], indent=2)); return
    if not args.model_dir or not args.out:
        parser.error("--model-dir and --out are required")
    encoder = OnnxEncoder(args.model_dir, threads=args.threads)
    report = run_comparison(encoder, args.out, input_path=args.input, repetitions=args.repetitions, count=args.documents,
                            progress=lambda p: print(json.dumps(p), flush=True))
    print(json.dumps(report["comparison"], indent=2))


if __name__ == "__main__":
    main()
