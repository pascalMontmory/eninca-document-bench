"""ENINCA documentary prototypes. No TPU implementation or speed claim."""
from .core import Document, Corpus, PrototypeClassifier, read_jsonl
from .encoder import OnnxEncoder

__all__ = ["Document", "Corpus", "PrototypeClassifier", "read_jsonl", "OnnxEncoder"]
