#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv
fi
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
if ! .venv/bin/python -c 'import numpy, onnxruntime, tokenizers; assert onnxruntime.__version__ == "1.31.0"; assert tokenizers.__version__ == "0.23.3"' 2>/dev/null; then
  .venv/bin/python -m pip install -e .
fi
model_dir="${ENINCA_DOCUMENT_MODEL:-.models/minilm}"
.venv/bin/python -m eninca_documents.cli fetch-model --model-dir "$model_dir"
.venv/bin/python scripts/verify_corpus.py
exec .venv/bin/python -m demo.server --model-dir "$model_dir" --open "$@"
