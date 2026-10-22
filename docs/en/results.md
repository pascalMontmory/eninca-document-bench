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

AMD EPYC-Milan VPS (Linux x86-64) and Mac (Darwin ARM64), two ONNX inference threads on each. Both runs use the same code, pinned model, corpus and timing sample of **48 documents / 591 windows**, spanning the training/validation length distribution. Three warm repetitions per configuration; setup and file I/O are excluded. The Mac report records `cpu_model: arm`, not a precise Apple chip designation.

| Chunk batch size | Order | VPS median | Mac median | VPS documents/s | Mac documents/s |
|---|---|---:|---:|---:|---:|
| 4 | Input | 22.661 s | 20.007 s | 2.118 | 2.399 |
| 4 | Length grouped | 21.554 s | **18.958 s** | 2.227 | **2.532** |
| 8 | Input | 21.557 s | 19.736 s | 2.227 | 2.432 |
| 8 | Length grouped | 20.672 s | 19.150 s | 2.322 | 2.507 |
| 16 | Input | 22.223 s | 19.929 s | 2.160 | 2.409 |
| 16 | Length grouped | **20.461 s** | 19.372 s | **2.346** | 2.478 |

All 18 timed outputs per machine passed chunk-order and embedding-tolerance checks. Process peak RSS was about **1,188 MiB on the VPS** and **1,389 MiB on the Mac**, including the model, retained arrays and warmups; these are process high-water marks, not isolated per-configuration measurements. The long-document corpus sharply reduces documents/s relative to the short synthetic fixture; windows/s and input length must accompany throughput claims.

On the Mac, grouping batch-4 windows by length reduces the median call time by **5.24%** against unsorted batch 4. The best observed configuration is grouped batch 4 on Mac (31.174 windows/s), versus grouped batch 16 on VPS (28.884 windows/s): **7.93% more throughput** when comparing each machine's observed best. For the same grouped batch-4 configuration the observed Mac throughput is 13.69% higher. These are different comparisons and neither isolates the CPU architecture: Python is 3.13.5 versus 3.11.2, NumPy 2.5.4 versus 2.4.6, and OS/hardware/load differ. ONNX Runtime 1.31.0 and Tokenizers 0.23.3 match. There is no independent performance-confirmation campaign or production cost-saving claim.

## Cross-machine quality and provenance

The Mac archive was imported byte-for-byte and verified against all **12 recorded source hashes**, the model identity, corpus manifest and three output hashes. Across the 80 held-out test documents, **all 80 decisions match under each policy**, including suggested labels and abstentions. The calibration thresholds and aggregate quality metrics also match. This confirms the same decisions for this fixed sample; the 90% validation precision target remains unmet on test (27/33 = 81.8%).

Cosine scores differ by at most **7.15 × 10⁻⁷** and margins by **1.07 × 10⁻⁶**. Floating results are therefore not bit-for-bit identical. Raw embedding arrays were not archived, so cross-machine embedding equality is not established. The imported archive contains four JSON/CSV files, not the terminal test log.

Mac evidence: [`report.json`](../../results/public-mac-20261022T110024Z/report.json), [`calibration.json`](../../results/public-mac-20261022T110024Z/calibration.json), [`quality.json`](../../results/public-mac-20261022T110024Z/quality.json), [`timings.csv`](../../results/public-mac-20261022T110024Z/timings.csv), [import receipt and archive hash](../../results/public-mac-20261022T110024Z/import.json). The [machine-readable comparison](../../results/mac-vps-public-comparison-20261022.json) can be recomputed offline with `python benchmarks/compare_cpu_records.py`; it compares archived evidence and runs no new inference.

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
