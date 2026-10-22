# Compare document-processing performance

[Français](../fr/comparison.md) · [Home](../../README.md) · [Evidence](../../results/index-comparison-20261022/)

The “Compare performance” screen helps decide whether to adopt a technical change for a given workload. It displays measured times, output checks, classification errors and files for recomputing the results. It does not yet compare our library against an external business application.

## Available result

22 October 2026, shared x86-64 AMD EPYC-Milan VPS CPU, two ONNX threads, pinned multilingual MiniLM:

| Metric | Input order | Length grouping |
|---|---:|---:|
| Median indexing time for 48 texts | 20.768 s | 20.833 s |
| Texts per second | 2.311 | 2.304 |
| Padding fraction | 3.027% | 0.215% |

**No confirmed speed gain in this run.** Seven pairs give a median speed ratio of 1.010 and a descriptive 95% interval of [0.958, 1.056], including 1. Five pairs are faster with grouping. Median paired time reduction is 0.95%, but variability prevents concluding a speed improvement. A ratio of medians and a median of paired ratios are different summaries and can have opposite signs.

All 80 classification decisions agree between configurations. The model accepts 33 suggestions, including 27 correct and **6 incorrect**, and abstains on 47 documents. Accepted precision is 81.8% (Wilson 95% interval: 65.6–91.4%). Three of twenty out-of-scope documents are incorrectly accepted. Preserving these decisions does not correct the model's errors.

This result supplements earlier Mac observations without replacing them. Different machines, timing boundaries and variability prevent a universal speedup claim.

A [second run through the web service](../../results/index-comparison-service-20261022/) also completed: 22.624 s reference and 22.125 s with grouping; median paired ratio 0.999, interval [0.935, 1.041], **again no confirmed gain**. All 80 decisions agree again. The service uses a 200% CPU quota and a 2 GiB memory limit. The two campaigns remain separate; the interface shows the last locally completed run.

## Use the screen

Run `bash demo.sh` and open the first tab. Archived evidence is displayed once the application is ready. It is labeled as an archived Linux x86-64 run, even when the browser runs on a Mac.

“Run a new comparison” executes both versions on the server host. A Mac browser connected to the VPS measures the VPS. It does not animate prerecorded results. Allow several minutes: the archived run took about eight minutes excluding model startup. Other application functions pause during measurement to avoid concurrent inference from this application; unrelated host workloads remain possible.

Cancellation takes effect between inference passes. The last completed report remains available after cancellation or failure. New results stay under `comparisons/` in the state directory and are not uploaded. CSV and ZIP downloads expose raw measurements.

The cost field stays empty until the operator supplies an hourly rate. The calculation is `median seconds / 48 × volume / 3600 × hourly rate`. This is conditional linear extrapolation, excluding human review, migration, OCR and remote storage. Negative differences remain negative. It does not demonstrate production savings.

## Protocol

- Same model, chunking, texts, resources and batch size four. Only grouping chunks by length changes; outputs are restored to original order.
- 48 texts selected from training/validation partitions, 591 chunks. IDs, hashes and execution order are written to `plan.json` before measurements.
- Two complete warmups, then seven pairs. AB/BA orders alternate in the plan before deterministic shuffling. No setting is chosen from the resulting timings.
- Synchronous indexing wall time: JSONL read, tokenization, CPU inference, pooling, validation and buffered index export. Model loading, warmup, output comparisons and temporary-file cleanup excluded. No `fsync`, network or remote storage.
- Every timed output checked against the reference: identical IDs, texts, chunks and encoder; vectors checked at `atol=rtol=3e-5`.
- Calibration on 80 validation documents frozen before evaluation on 80 separate test documents. Decisions and errors checked in both versions. Retrieval quality and human correction time remain unmeasured.
- Descriptive interval from 10,000 resamples of complete pairs. Seven repetitions on identical texts do not cover business-corpus variability or all shared-host drift. These data have already been used in earlier experiments.

Peak memory covers the whole process, including reference arrays and any preloaded indexes; it is not a per-variant memory comparison. The archived run used the CLI; the demonstration service may have its own resource limits. Preserve execution context when comparing campaigns.

## Run or verify without a browser

From the repository root after installation and model download:

```bash
PYTHONPATH=src .venv/bin/python -m benchmarks.comparison \
  --model-dir .models/minilm --out runs/comparison-new
PYTHONPATH=src .venv/bin/python -m benchmarks.comparison \
  --verify results/index-comparison-20261022
PYTHONPATH=src .venv/bin/python -m benchmarks.check_comparison_record \
  results/index-comparison-20261022
```

The final check also recomputes quality metrics from recorded predictions and public labels, and checks source provenance. Hashes detect inconsistency; they are not external signatures.

For an authorized local dataset, supply at least 48 JSONL objects with unique `id` and nonempty `text`:

```bash
PYTHONPATH=src .venv/bin/python -m benchmarks.comparison \
  --model-dir .models/minilm --input private-data/documents.jsonl \
  --documents 48 --out runs/comparison-private
```

This checks outputs and timing but reports **business quality not evaluated**. Reports contain IDs and hashes; keep them within the authorized boundary. The web demonstration exposes no private-document upload.

## Make a business decision

A pilot needs representative data, independent expected answers, current-process time and human-review time. Compare equal scopes: initial extraction, model, text lengths, resources and storage. Set acceptable precision, false-positive, latency and cost thresholds in advance. Keeping the existing system is a valid outcome.

No industrial, OCR, TPU or GPU gain is established here.

© 2026 ENINCA CONSULTING — All rights reserved in original code and project documentation. Third-party rights remain separate.
