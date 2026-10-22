from pathlib import Path
import argparse
import hashlib
import json

from eninca_documents import Corpus, Document, OnnxEncoder, PrototypeClassifier, read_jsonl
from eninca_documents.cli import provenance


parser = argparse.ArgumentParser()
parser.add_argument('--model-dir', required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parent
data = json.loads((root / 'challenge.json').read_text())
encoder = OnnxEncoder(args.model_dir, batch_size=8, threads=2)
corpus = Corpus.load(root / 'results/demo/index')
queries = []
for query in data['queries']:
    hits = corpus.search(encoder.encode_query(query['text']), encoder_identity=encoder.identity, top_k=3)
    queries.append({**query, 'hits': hits, 'top1_correct': hits[0]['document_id'] == query['expected_id']})
training = encoder.encode_documents(read_jsonl(root / 'eninca-documents/examples/training.jsonl'))
documents = [Document(d['id'], d['text']) for d in data['documents']]
predictions = PrototypeClassifier(training).predict(encoder.encode_documents(documents))
checks = [{**d, 'prediction': p, 'correct': d['expected_label'] == p['label']}
          for d, p in zip(data['documents'], predictions)]
known = [c for c in checks if c['expected_label'] is not None]
unknown = [c for c in checks if c['expected_label'] is None]
summary = {'new_query_top1_correct': sum(q['top1_correct'] for q in queries), 'new_queries': len(queries),
           'known_class_correct': sum(c['correct'] for c in known), 'known_class_documents': len(known),
           'unknown_correctly_sent_for_review': sum(c['correct'] for c in unknown), 'unknown_documents': len(unknown)}
report = {'environment': provenance(), 'encoder': encoder.identity,
          'challenge_sha256': hashlib.sha256((root / 'challenge.json').read_bytes()).hexdigest(),
          'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'thresholds': {'min_score': .4, 'min_margin': .05},
          'scope': data['description'], 'summary': summary, 'queries': queries, 'classification': checks}
with (root / 'results/challenge-report.json').open('x') as f:
    json.dump(report, f, ensure_ascii=False, indent=2, allow_nan=False)
print(json.dumps(summary, indent=2))
for check in checks:
    if not check['correct']:
        print('Unexpected classification:', json.dumps(check, ensure_ascii=False))
