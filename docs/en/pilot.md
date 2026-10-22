# A small documentary pilot

[Français](../fr/pilot.md) · [Home](../../README.md)

The useful deliverable is a measured answer to one operational question: can a local search or assisted-routing step save review time at acceptable quality and cost?

1. Choose one task and a currently used baseline: search by meaning, or routing into a few document categories. Start with extracted text. OCR and image parsing are separate scope.
2. Agree permitted deployment, data handling and evaluation rights. Use public, synthetic or appropriately authorized data. Nothing in this kit transmits documents automatically; exported indexes and reports can still contain sensitive text.
3. Prepare a few hundred labeled examples plus realistic out-of-scope cases. Split by source dossier, template or time period before chunking, with distinct training, validation and final test. Keep the final labels away from threshold selection. This size is a feasibility study, not industrial certification.
4. Agree success criteria before testing: accepted-classification precision **and** coverage, unknown false acceptance, review time, retrieval relevance, latency, throughput, peak memory and operational costs. Set thresholds according to the risk of the particular workflow; 90% in this research kit is only a demonstration policy.
5. Deliver a reproducible run, failure examples, a comparison with the existing process and an explicit continue/stop recommendation. Native hardware costs, startup, transfers and integration effort belong in the cost estimate. A negative result is useful and must remain visible.

The initial technical package already provides the local encoder, retrieval API, classification API, an abstention-calibration procedure, a public-data benchmark, raw evidence and Mac/Linux commands. The pilot adds task-specific labels, reference process and acceptance criteria. It does not require committing to a TPU migration.

The scope and price of a paid feasibility study can be agreed separately with ENINCA CONSULTING. This repository is not a quotation, an activated evaluation license, a compliance certification or a promise of savings.
