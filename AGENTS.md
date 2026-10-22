# Maintenance rules

- Keep this repository generic and independent of any prospective customer. Do not add customer identities, private documents, credentials or private legal records.
- Keep user documentation in English and French with matching claims.
- Do not convert CPU observations into TPU/GPU performance or industrial-quality claims.
- Preserve source/data/model provenance and explicit limitations. Never tune on final evaluation labels.
- Keep historical evidence tied to its frozen source. Rerun an affected campaign before presenting changed code as its measured implementation.
- Model weights, private data, generated indexes and Python environments stay outside Git. Original and third-party rights remain distinct.
- Run unit contracts and `scripts/check_records.py` before delivery; use the pinned model for native inference changes.
