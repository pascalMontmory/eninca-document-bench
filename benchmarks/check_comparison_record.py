"""Recompute public comparison summaries and check their source/data provenance."""
import argparse
import csv
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import statistics

import numpy as np

from benchmarks.comparison import ROOT, VARIANTS, sha, verify_report
from eninca_documents.calibration import decision_metrics
from eninca_documents.core import read_jsonl


def check(directory):
    directory = Path(directory)
    report = verify_report(directory)
    plan = json.loads((directory / "plan.json").read_text())
    if plan != report["plan"]:
        raise ValueError("Embedded plan differs from frozen plan")
    for relative, digest in plan["source_sha256"].items():
        path = (ROOT / relative).resolve()
        if not path.is_relative_to(ROOT) or sha(path) != digest:
            raise ValueError(f"Source changed: {relative}; use the recorded source revision")
    rows = list(csv.DictReader((directory / "timings.csv").open(newline="")))
    expected_order = [(pair, position, variant) for pair, order in enumerate(plan["pair_orders"], 1)
                      for position, variant in enumerate(order, 1)]
    if [(int(r["pair"]), int(r["position"]), r["variant"]) for r in rows] != expected_order:
        raise ValueError("Execution order differs from plan")
    for variant in VARIANTS:
        current = [r for r in rows if r["variant"] == variant]
        times = [float(r["index_seconds"]) for r in current]
        median = statistics.median(times)
        expected = dict(median_index_seconds=median, min_index_seconds=min(times), max_index_seconds=max(times),
                        median_encode_seconds=statistics.median(float(r["encode_seconds"]) for r in current),
                        median_export_seconds=statistics.median(float(r["export_seconds"]) for r in current),
                        documents_per_second=report["documents"]/median, chunks_per_second=report["chunks"]/median,
                        padding_fraction=1-int(current[0]["tokens"])/int(current[0]["padded_tokens"]))
        if expected != report["variants"][variant]:
            raise ValueError("Variant metrics differ from CSV")
        if any(int(r["documents"]) != report["documents"] or int(r["chunks"]) != report["chunks"] for r in current):
            raise ValueError("Workload changed between passes")
    if plan["input_kind"] == "public_dila":
        data = ROOT / "data/dila-v1"
        if sha(data / "manifest.json") != plan["input_sha256"]:
            raise ValueError("Public manifest mismatch")
        for name, digest in json.loads((data / "manifest.json").read_text())["files"].items():
            if Path(name).name != name or sha(data / name) != digest:
                raise ValueError("Public corpus mismatch")
        train = read_jsonl(data / "train.jsonl")
        validation = read_jsonl(data / "validation.jsonl")
        documents = read_jsonl(data / "test.jsonl")
        candidates = sorted(train + validation, key=lambda d: (len(d.text), d.id))
        chosen = [candidates[i] for i in np.linspace(0, len(candidates)-1, report["documents"], dtype=int)]
        selected = [chosen[i] for i in np.random.default_rng(20261023).permutation(len(chosen))]
        digest = hashlib.sha256(json.dumps([asdict(d) for d in selected], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        if [d.id for d in selected] != plan["timing_document_ids"] or digest != plan["selected_texts_sha256"]:
            raise ValueError("Selected texts mismatch")
        predictions = json.loads((directory / "predictions.json").read_text())
        fields = ("document_id", "suggested_label", "label", "needs_review")
        matches = sum(all(a[k] == b[k] for k in fields) for a, b in zip(predictions["reference"], predictions["optimized"]))
        if matches != len(documents) or matches != report["quality"]["matching_decisions"]:
            raise ValueError("Classification agreement mismatch")
        for name in ("reference", "optimized"):
            if decision_metrics(documents, predictions[name], {d.label for d in train}) != report["quality"][name]:
                raise ValueError("Quality metrics differ from public labels")
    elif report["quality"]["status"] != "not_evaluated":
        raise ValueError("Unsupported business-quality claim")
    return dict(status="pass", pairs=report["comparison"]["pairs"],
                verdict=report["comparison"]["verdict"], source_files=len(plan["source_sha256"]),
                checks=["source_and_output_hashes", "frozen_plan", "csv_metrics", "paired_summary",
                        "public_quality_and_selected_texts" if plan["input_kind"] == "public_dila" else "no_business_quality_claim"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory")
    print(json.dumps(check(parser.parse_args().directory), indent=2))
