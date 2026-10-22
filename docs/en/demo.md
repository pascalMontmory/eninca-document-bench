# Local document demonstration

[Français](../fr/demo.md) · [Home](../../README.md)

**© 2026 ENINCA CONSULTING — All rights reserved.** Original code and project-specific documentation are the property of ENINCA CONSULTING. DILA data, the MiniLM model and dependencies retain their respective rights. See [LICENSE](../../LICENSE) and [third-party notices](../../THIRD_PARTY_NOTICES.md).

## Start on the Mac

From an existing Git checkout:

```bash
cd ~/Downloads/eninca-document-bench
git pull --ff-only
bash demo.sh
```

An archive-based folder has no `.git` directory: download and extract the new archive instead of `git pull`, preserving `.venv`, `.models` and `runs`. For a new folder, clone the public repository and run `bash demo.sh`.

Python 3.11 or newer is required. The launcher reuses `.venv` and `.models/minilm`. If missing, it installs dependencies and explicitly downloads the pinned model, approximately 479 MB. To reuse a model from another folder:

```bash
ENINCA_DOCUMENT_MODEL="$HOME/Downloads/eninca-documents/.models/minilm" bash demo.sh
```

Open **http://127.0.0.1:8765** if the browser does not open automatically. Keep the Terminal open. Double-clicking `demo.command` is also possible after setup. **Ctrl+C** stops the server. If the port is occupied: `bash demo.sh --port 8766`, then use the printed address.

Preparation encodes 60 training, 80 validation and 80 test documents. The interface shows progress. Encoding can take several minutes depending on the machine. Subsequent launches load indexes and recompute centroids and calibration without re-encoding. Loading follows the same numerical path as on first launch.

## A five-minute presentation

Prepare the index before the meeting. To start without human decisions, use fresh state: `bash demo.sh --state-dir runs/demo-presentation`. This new state needs its own initial indexing.

1. **Search, one minute.** Click “Rental housing” or ask a short question. Open a result: excerpt, full text and source are available. This searches existing text; it does not generate an answer. The score is similarity, not a probability.
2. **Classification, two minutes.** Open “Classify and review”, then “Abstentions awaiting review”. Read a document, choose a topic or “Outside the four topics”, and save. Also show that an automatically accepted suggestion can be corrected. An automatic suggestion is never presented as human approval.
3. **Summary, one minute.** Show decisions, documents awaiting review and corrected suggestions. Initial model results stay separate: human review does not artificially improve them.
4. **Export, one minute.** Download the CSV: original suggestion, human decision, date and configuration identifier. All 80 rows are exported, including those without a decision. In “Saved decisions”, a decision can be changed or returned to review.

The interface can switch languages; DILA documents remain French. Examples are not a retrieval-quality test: relevance needs independent evaluation questions before any commercial promise.

## Read the counters

- **Search: 220 documents**, across all three partitions. Reference labels are not used for retrieval.
- **Review: 80 test documents.** Training and calibration use only their respective partitions. Human corrections do not retrain them.
- **Awaiting review**: no human decision, even if the model accepted its suggestion. **Abstentions awaiting review**: the subset where the model abstained.
- **Corrected suggestions**: human decision different from the top suggested topic, including out of scope. This overlaps the out-of-scope count; the four cards are not additive.
- **Automatic precision**: automatically accepted suggestions that are correct according to public reference labels, divided by all accepted suggestions. It is neither coverage nor human decision accuracy. The interval and out-of-scope false accepts are displayed.
- **Times**: session preparation, original encoding retained in the cache, and this session’s searches. Loading a cache is not a newly timed encoding.

Configuration uses batch size four, length sorting and two CPU threads. This choice from the small Mac experiment is not a guaranteed optimum. Historical benchmarks remain in [results](results.md); the demonstration computes its own results with the local model.

## Operation and persistence

The server listens only on `127.0.0.1`. It exposes no private-document upload, data submission, telemetry or external AI calls. Fonts and scripts are local. Source and repository links intentionally open an external site. This single-user demonstration server must not be exposed to the Internet.

`runs/browser-demo/indexes/` contains texts and embeddings; `reviews.sqlite3` retains every decision revision, including returns to review. These files are excluded from Git. Cache keys include model identity, corpus, library source and dependency versions. A changed prediction configuration uses a separate decision scope without silently applying earlier corrections.

Checksums detect accidental corruption; they are neither signatures nor legal proof. If a cache is rejected, stop the server and rename the affected `indexes` subdirectory to preserve it before rebuilding. Back up the state directory to preserve decisions. A second process cannot use the same directory. Concurrent tabs cannot silently overwrite a newer decision.

## Checks

```bash
ENINCA_DOCUMENT_MODEL=.models/minilm .venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/check_records.py
```

New tests cover caching, persistence, concurrent-tab conflicts, undo, configuration isolation, export and local HTTP protections. The optional browser check uses an existing Playwright and Chromium installation; these are not needed for ordinary use:

```bash
python demo/check_browser.py --url http://127.0.0.1:8765 --out runs/browser-check
```

This checks real-model search, review, export, both languages and mobile layout. It adds then undoes a decision: use separate state if you want another history without those events. Restart checking is separate. **These CPU checks demonstrate no TPU/GPU or industrial gain.** GitHub CI remains disabled.
