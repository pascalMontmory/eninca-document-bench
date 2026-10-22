# ENINCA Document Bench

[Français](README.fr.md) · [Methods](docs/en/methodology.md) · [Results](docs/en/results.md) · [Pilot](docs/en/pilot.md)

A local Python library for document search, assisted classification and reproducible CPU evaluation. Developed by Pascal Montmory for **ENINCA CONSULTING**.

**© 2026 ENINCA CONSULTING — All rights reserved. The original integration code and project-specific documentation are the property of ENINCA CONSULTING.** Public access does not grant a general license to use these contributions. Third-party models, software and public data retain their own rights. See [LICENSE](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md).

The practical objective is to establish document quality, human-review workload and processing cost before investing in accelerator-specific development. This is a working CPU prototype and evaluation kit, not a deployed document-management system.

## What works today

- Semantic search with document-level deduplication and excerpts from the original text.
- Class centroids learned from labeled examples, with an explicit human-review decision.
- Abstention thresholds selected on separate validation documents, including out-of-scope topics.
- Long-text chunking without silently dropping the end of documents.
- A frozen, attributed set of **220 public French administrative documents** from Service Public / DILA: 60 training, 80 validation, 80 test; 107 parent dossier families kept separate across splits.
- Warm CPU batching measurements, checked embeddings, raw CSV, model/source/data hashes and tests.

**No OCR, native TPU/GPU encoder or production cost reduction is demonstrated.** The current model runs through ONNX Runtime on CPU. The public corpus contains guidance pages, not scans or real business correspondence. Pallas/TPU is a separate future evaluation, not an enabled backend.

## Start on macOS or Linux

Python 3.11 or newer is required. The model download is about 479 MB; allow additional space for the Python environment. Only dependency installation and the explicit model-download command need network access.

```bash
git clone https://github.com/pascalMontmory/eninca-document-bench.git
cd eninca-document-bench
bash run.sh
```

The repository is publicly readable and can be cloned without GitHub authentication. The script installs the library, downloads and verifies the pinned model, runs tests, then performs the public-data CPU benchmark. It writes a new `runs/<timestamp>-public-cpu/` directory. The full campaign can take several minutes depending on the machine; progress is printed. **It uploads nothing.**

Reuse an existing model cache with `ENINCA_DOCUMENT_MODEL=/path/to/model bash run.sh`. If using the earlier Mac kit, that cache is normally `~/Downloads/eninca-documents/.models/minilm`; verify the path exists first.

For the short synthetic demonstration after setup:

```bash
.venv/bin/eninca-documents demo --model-dir .models/minilm \
  --data-dir examples --out runs/demo --repetitions 3
```

Output paths must be new; existing results are not overwritten.

## Try your own texts

Use UTF-8 JSONL, one object per line. Labels are optional for indexing and inference, required for training and validation.

```json
{"id":"document-001","text":"Le texte complet extrait du document.","label":"facture"}
```

```bash
.venv/bin/eninca-documents index --model-dir .models/minilm \
  --input private-data/documents.jsonl --out runs/my-index
.venv/bin/eninca-documents search --model-dir .models/minilm \
  --index runs/my-index --query "Quelle facture doit être réglée ?"
```

For assisted classification with separate validation:

```bash
.venv/bin/python scripts/assisted_classify.py --model-dir .models/minilm \
  --training private-data/train.jsonl --validation private-data/validation.jsonl \
  --input private-data/new-documents.jsonl --out runs/classification
```

Validation must include labeled examples from topics absent from training. The default validation objective is 90% empirical precision among accepted predictions, with at least five accepted examples. This is **not a guarantee** on new documents. If no threshold meets the objective, every document is sent for review. Text/ID overlap is rejected; the operator must also separate document families, templates and duplicates when preparing private data.

## Evidence and limits

Read [the measured results and failures](docs/en/results.md), [the exact protocol](docs/en/methodology.md) and [a small pilot specification](docs/en/pilot.md). Historical Mac ARM64 and VPS x86-64 runs are retained with the frozen source that generated them. Floating embeddings are checked with numerical tolerances; no bit-for-bit cross-architecture claim is made.

The encoder is the existing multilingual MiniLM model, not a newly trained ENINCA model. Retrieval is in-memory exact cosine search; it is not a million-document vector database. Long documents are averaged over overlapping chunks for classification, which can dilute a local topic. Cosine scores and margins are not probabilities. Index exports contain full text; treat them as confidential when using private documents.

The CI workflow is prepared to check unit contracts, split isolation and evidence consistency. It is currently disabled on GitHub. Once re-enabled, it also supports optional native model checks through manual workflow dispatch; the recorded local CPU run includes them. No CI performance numbers are advertised.

**Hosted CI status, 22 October 2026:** [the first run](https://github.com/pascalMontmory/eninca-document-bench/actions/runs/39766001763) was blocked before any tests started. GitHub reported a recent-payment or spending-limit issue on the account. The workflow was then disabled at the repository owner's request. The 19 native tests and evidence checks passed locally; no successful hosted run is claimed.

## Rights

Original integration code was developed for ENINCA CONSULTING. Access does not grant a general open-source or production license; see [LICENSE](LICENSE). Model, dependencies and DILA data retain their own rights and attribution: [third-party notices](THIRD_PARTY_NOTICES.md). No private legal documents are included.
