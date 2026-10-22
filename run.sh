#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install -e .
model_dir="${ENINCA_DOCUMENT_MODEL:-.models/minilm}"
.venv/bin/python -m eninca_documents.cli fetch-model --model-dir "$model_dir"
ENINCA_DOCUMENT_MODEL="$model_dir" .venv/bin/python -m unittest discover -s tests -v
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
out="runs/${stamp}-public-cpu"
.venv/bin/python benchmarks/run_public.py --model-dir "$model_dir" --out "$out"
printf '\nResults / Résultats : %s\n' "$out"
