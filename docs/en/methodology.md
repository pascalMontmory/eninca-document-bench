# Evaluation protocol

[Français](../fr/methodology.md) · [Home](../../README.md)

## Public-data quality evaluation

The fixed DILA snapshot was retrieved on 22 October 2026. The [manifest](../../data/dila-v1/manifest.json) records the upstream archive hash, XML hashes, individual update dates, attribution URLs, labels, parent dossier families and split assignments. The selected XML files are included so extraction can be checked without relying on a changing `latest.zip` URL. Run `python scripts/verify_corpus.py` to verify them.

Only practical-information files with 500–12,000 extracted Unicode characters are eligible. This excludes very short and very long pages; it does not truncate retained texts. Title and article body are retained. Navigation, theme metadata, breadcrumbs and related-page lists are excluded from encoded text. Whitespace is normalized during this XML-to-text conversion. The library subsequently preserves the resulting text and Unicode excerpt offsets.

Four source themes are treated as known classes: money/tax/consumption (`N19803`), work/training (`N19806`), housing (`N19808`), social/health (`N19811`). Identity/citizenship (`N19810`) and transport (`N19812`) are held out as unknown topics. Editorial topic labels are a proxy for routing, not invoice/contract ground truth.

Parent dossier families are assigned to splits before document selection, in a deterministic SHA-256 order. No family occurs in multiple splits. Known themes have 15 examples per split; unknown themes have 10 examples each in validation and test only. Five-word shingle Jaccard similarity of at least 0.70 rejects near duplicates among selected texts. Related topics can still overlap semantically. Neither data selection nor split assignment uses model outputs.

Training consists only of computing normalized class centroids from 60 document embeddings; the pretrained transformer is not fine-tuned. Each document embedding is the normalized mean of its chunk embeddings. Chunks overlap by 16 tokens and contain at most 128 tokens including two special tokens. A token represented in overlapping windows contributes more than once.

Threshold selection uses the 80 validation documents. The grid contains 39 minimum scores between 0 and 0.95 and 31 margins between 0 and 0.30. Candidate policies must accept at least five documents and attain 90% empirical accepted precision; accepting an unknown topic counts as an error. Among eligible policies choose the greatest known-class coverage, then greatest accepted precision, then stricter score/margin thresholds. If none qualifies, reject all. The policy is written before test encoding and never retuned using test results.

The final 80-document test compares that policy with the original uncalibrated defaults (score 0.4, margin 0.05). Report accepted counts, errors, known-class coverage/accuracy and unknown false acceptance. Precision is undefined when nothing is accepted. Wilson intervals are descriptive approximations, not a guarantee or a correction for correlated document families or threshold selection. Repeating inference never increases the statistical sample size.

## CPU measurements

The transformer/model revision and all model files are pinned and checked by SHA-256. Backend: `CPUExecutionProvider`; intra-op threads: 2; inter-op threads: 1; sequential ONNX execution. Record Python, NumPy, ONNX Runtime, Tokenizers, CPU, OS and logical CPU count in each report.

The full quality dataset is encoded once per split. Timing uses 48 documents selected evenly across character lengths from training plus validation, without test documents. Six configurations are compared: chunk batch sizes 4, 8, 16, each in input order or grouped by length. All configurations are warmed; measurement order is pseudorandomized with a fixed schedule in each of three repetitions.

Every timed result is compared to the input-order batch-4 reference: identical chunk identities/order, embeddings within `atol=rtol=3e-5`. Comparisons are outside the timer. Reports contain each synchronous call time, tokenization/inference/pooling times, token/padding counts, extrema, medians, documents/s and chunks/s. Model loading/hashing, file reads, exports and comparisons are excluded from these warm call timings. Model setup and initial quality encodings are separately reported. The cumulative process peak RSS includes retained arrays and warmups; it is not an isolated memory measurement per configuration.

Three repeats on a shared VPS are exploratory measurements. The fastest measured configuration has not received a separate performance-confirmation campaign. Do not extrapolate documents/s without accounting for document length, chunk count, machine, concurrency and input/output costs. Model download and startup matter for short one-shot tasks.

## Reproduce

```bash
python -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/eninca-documents fetch-model --model-dir .models/minilm
ENINCA_DOCUMENT_MODEL=.models/minilm .venv/bin/python -m unittest discover -s tests -v
.venv/bin/python benchmarks/run_public.py --model-dir .models/minilm --out runs/public-check
.venv/bin/python scripts/check_records.py
python benchmarks/compare_cpu_records.py
```

`report.json` identifies sources and data; `calibration.json` records the selected policy and validation IDs; `quality.json` retains every prediction; `timings.csv` retains raw measurements. Source changes require a new named evidence run or an explicit historical source snapshot; never edit old measurements to appear current.

## TPU work that remains

The PRNG/Pallas research is a different workload. It does not demonstrate faster transformer inference. A future encoder port must match tokenization, all chunks, masks, pooling and model weights; compare embeddings, rankings and classification decisions with tolerances appropriate to the chosen precision. Establish an ordinary JAX baseline, inspect end-to-end profiling, then consider targeted Pallas kernels. Include data movement, compilation, throughput, quality and actual infrastructure cost. Native TPU access is required for TPU performance claims.
