# Measured results and limitations

[Français](../fr/results.md) · [Methods](methodology.md) · [Home](../../README.md)

## Public French corpus — 22 October 2026

220 DILA guidance documents, 107 parent dossier families, four known topics and two unknown topics. Training: 60 documents. Validation: 80. Final test: **80**, including 20 unknown-topic documents. This is a public-data routing proxy, not a customer evaluation or an OCR task.

| Held-out test result | Original fixed thresholds | Validation-calibrated thresholds |
|---|---:|---:|
| Accepted decisions | 57 / 80 | 33 / 80 |
| Correct accepted decisions | 38 / 57 | 27 / 33 |
| Accepted precision | 66.7% | **81.8%** |
| Documents sent for review | 23 / 80 | **47 / 80** |
| Known-topic coverage | 44 / 60 (73.3%) | 30 / 60 (50.0%) |
| Unknown topics wrongly accepted | 13 / 20 (65.0%) | **3 / 20 (15.0%)** |
| Known-topic accuracy, abstentions counted as errors | 38 / 60 (63.3%) | 27 / 60 (45.0%) |

The policy selected on validation has minimum cosine score approximately **0.75** and margin **0.01**. Its validation precision was 27/30 = 90%. **That target did not generalize to the test set**: test accepted precision is 27/33 = 81.8%, with a descriptive Wilson 95% interval of approximately 65.6–91.4%. The unknown false-acceptance interval is approximately 5.2–36.0%. These small-sample intervals are not production guarantees and do not account for document-family correlation.

The tradeoff is explicit: fewer wrong unknown acceptances and better accepted precision, but more human review and fewer correctly handled known documents overall. Six test decisions remain wrong among the 33 accepted. Do not present this as autonomous classification or reuse the selected thresholds as universal values. Improve task-specific training coverage and validation in a new, separately evaluated protocol.

Raw records: [`report.json`](../../results/public-cpu-20261022/report.json), [`calibration.json`](../../results/public-cpu-20261022/calibration.json), [`quality.json`](../../results/public-cpu-20261022/quality.json), [`timings.csv`](../../results/public-cpu-20261022/timings.csv), [`run.log`](../../results/public-cpu-20261022/run.log). Each prediction, including rejected and incorrect cases, is retained. DILA editorial themes may overlap semantically; inspecting failures matters.

## CPU batching on the public corpus

AMD EPYC-Milan VPS, Linux x86-64, two ONNX inference threads. The timing sample contains **48 documents / 591 windows**, spanning the training/validation length distribution. Three warm repetitions per configuration; setup and file I/O are excluded.

| Chunk batch size | Order | Median call time | Documents/s | Windows/s |
|---|---|---:|---:|---:|
| 4 | Input | 22.661 s | 2.118 | 26.080 |
| 4 | Length grouped | 21.554 s | 2.227 | 27.419 |
| 8 | Input | 21.557 s | 2.227 | 27.415 |
| 8 | Length grouped | 20.672 s | 2.322 | 28.590 |
| 16 | Input | 22.223 s | 2.160 | 26.594 |
| 16 | Length grouped | 20.461 s | 2.346 | 28.884 |

All 18 timed outputs passed chunk-order and embedding-tolerance checks. Process peak RSS was about **1,188 MiB**, including the model, retained arrays and warmups. This is an exploratory configuration comparison, without a separate confirmation campaign or evidence of a production cost saving. The long-document corpus sharply reduces documents/s relative to the short synthetic fixture; windows/s and input length must accompany throughput claims.

## Earlier small synthetic demonstration

| Observation | Mac ARM64 CPU | VPS x86-64 CPU |
|---|---:|---:|
| Documents / chunks in timing | 12 / 13 | 12 / 13 |
| Median input-order encoding | 0.315548 s | 0.374635 s |
| Median length-grouped encoding | 0.252202 s | 0.291689 s |
| Length-grouped documents/s | 47.58 | 41.14 |
| Retrieval: correct top-1 / queries | 7 / 8 | 7 / 8 |
| Retrieval: recall at 3 | 100% | 100% |
| Original classification fixture | 8 / 8 | 8 / 8 |

Source: [Mac record](../../results/historical/mac-smoke.json), [VPS record](../../results/historical/vps-smoke.json), [frozen encoder source](../../evidence/encoder-v0.1.0). Three timing repetitions and very small authored fixtures. Different Python/NumPy versions and machine conditions prevent a controlled architecture-only comparison. No cross-machine raw embedding equality is demonstrated.

The [additional challenge](../../results/historical/challenge.json) exposed a commercial lease wrongly accepted as an invoice, and a known-topic document sent for review. It had 3/4 new retrieval queries correct at rank 1, 7/8 known classifications correct, and only 1/2 unknown documents correctly rejected. These failures motivated validation and out-of-scope evaluation; they were not reused to tune the public-corpus policy.

## Scope of conclusions

Functional CPU execution and reproducible measurements are demonstrated. Native tests exercise long Unicode texts, padding, batch-order invariance and query-length rejection. They do not establish an industrial service level. Public-corpus results cannot be compared directly with the short synthetic documents/s figures: the long texts require many more windows.

No measured TPU/GPU encoder speed, end-to-end OCR improvement, million-document scalability, cloud-cost saving or compliance certification is claimed. Original model/dependency attributions remain in [third-party notices](../../THIRD_PARTY_NOTICES.md).
