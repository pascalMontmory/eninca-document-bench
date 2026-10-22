"""Check archived evidence against frozen sources; no new performance measurements."""
import csv
import hashlib
import json
import statistics
from pathlib import Path

from verify_corpus import verify
from eninca_documents.core import read_jsonl
from eninca_documents.calibration import decision_metrics

ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    print(verify(ROOT/'data/dila-v1'))
    for path in sorted((ROOT/'results/historical').glob('*.json')):
        report=json.loads(path.read_text())
        for name, expected in report['environment']['source_sha256'].items():
            assert sha(ROOT/'evidence/encoder-v0.1.0'/name)==expected, (path,name)
        for name,expected in report.get('data_sha256',{}).items():
            assert sha(ROOT/'examples'/name)==expected,(path,name)
        if 'challenge_sha256' in report:
            assert sha(ROOT/'examples/challenge.json')==report['challenge_sha256']
            assert sha(ROOT/'evidence/challenge-v0.1.0.py')==report['runner_sha256']
        print(path.relative_to(ROOT),'frozen source hashes PASS')
    reports=list((ROOT/'results').glob('public-*/report.json'))
    if not reports:
        raise ValueError('Missing public-corpus evidence')
    for path in reports:
        report=json.loads(path.read_text())
        assert report['status']=='pass' and report['tpu_tested'] is False
        assert sha(ROOT/'data/dila-v1/manifest.json')==report['data_manifest_sha256']
        for name,expected in report['source_sha256'].items():
            assert sha(ROOT/name)==expected,(path,name)
        for name,expected in report['outputs_sha256'].items():
            assert sha(path.parent/name)==expected,(path,name)
        rows=list(csv.DictReader((path.parent/'timings.csv').open()))
        assert len(rows)==6*report['repetitions']
        assert all(float(r['caller_seconds'])>0 for r in rows)
        assert len(report['timing_document_ids'])==len(set(report['timing_document_ids']))==report['timing_documents']
        for summary in report['summary']:
            selected=[r for r in rows if int(r['batch_size'])==summary['batch_size'] and
                      (r['sort_by_length']=='True')==summary['sort_by_length']]
            median=statistics.median(float(r['caller_seconds']) for r in selected)
            assert abs(median-summary['median_seconds']) < 1e-12
            assert abs(report['timing_documents']/median-summary['documents_per_second']) < 1e-12
        quality=json.loads((path.parent/'quality.json').read_text())
        documents=read_jsonl(ROOT/'data/dila-v1/test.jsonl')
        manifest=json.loads((ROOT/'data/dila-v1/manifest.json').read_text())
        for name,field in [('fixed_defaults','fixed_default_predictions'),('validation_calibrated','predictions')]:
            assert decision_metrics(documents,quality[field],manifest['known_labels'])==report['quality'][name]
        policy=json.loads((path.parent/'calibration.json').read_text())
        assert {r['id'] for r in policy['validation_documents']}=={d.id for d in read_jsonl(ROOT/'data/dila-v1/validation.jsonl')}
        print(path.relative_to(ROOT),'source, data and output hashes PASS')


if __name__=='__main__':
    main()
