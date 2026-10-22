"""Frozen-data CPU benchmark. Never times an emulated TPU or selects on test quality."""
import argparse
import csv
import hashlib
import json
import resource
import statistics
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from verify_corpus import verify
from eninca_documents.core import PrototypeClassifier, read_jsonl
from eninca_documents.encoder import OnnxEncoder
from eninca_documents.calibration import calibrate, predict_calibrated, decision_metrics
from eninca_documents.cli import provenance, write_json


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-dir', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--threads', type=int, default=2)
    parser.add_argument('--repetitions', type=int, default=3)
    parser.add_argument('--timing-documents', type=int, default=48)
    args = parser.parse_args()
    if args.repetitions < 3 or args.timing_documents < 6 or args.timing_documents > 140:
        raise ValueError('Use at least 3 repetitions and 6..140 timing documents')
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    data = ROOT / 'data/dila-v1'
    checks = verify(data)
    print(f'Corpus: {checks}', flush=True)
    encoder = OnnxEncoder(args.model_dir, threads=args.threads)
    sets = {split:read_jsonl(data / (split+'.jsonl')) for split in ['train','validation','test']}
    encoded = {}
    for split in ['train','validation']:
        print(f'Encoding {split}: {len(sets[split])} documents', flush=True)
        encoded[split] = encoder.encode_documents(sets[split])
    classifier = PrototypeClassifier(encoded['train'])
    policy = calibrate(classifier, encoded['validation'])
    write_json(out / 'calibration.json', policy)  # frozen before first test inference
    print(f'Calibration frozen: {policy["mode"]}, score={policy["min_score"]}, margin={policy["min_margin"]}', flush=True)
    encoded['test'] = encoder.encode_documents(sets['test'])
    raw_predictions = classifier.predict(encoded['test'], min_score=.4, min_margin=.05)
    predictions = predict_calibrated(classifier, encoded['test'], policy)
    quality = {'fixed_defaults':decision_metrics(sets['test'],raw_predictions,classifier.labels),
               'validation_calibrated':decision_metrics(sets['test'],predictions,classifier.labels)}
    write_json(out / 'quality.json', {'test':quality, 'predictions':predictions,
                                   'fixed_default_predictions':raw_predictions})
    print('Held-out quality: '+json.dumps(quality), flush=True)
    # Stratify timings by length across train+validation only; no test-based tuning.
    candidates = sorted(sets['train']+sets['validation'],key=lambda d:(len(d.text),d.id))
    selected = [candidates[i] for i in np.linspace(0,len(candidates)-1,args.timing_documents,dtype=int)]
    configurations = [(batch, ordered) for batch in [4,8,16] for ordered in [False,True]]
    reference = None
    for batch, ordered in configurations:
        print(f'Warmup: batch={batch}, length_sorted={ordered}',flush=True)
        encoder.batch_size, encoder.sort_by_length = batch, ordered
        current = encoder.encode_documents(selected)
        if reference is None:
            reference = current
        if current.chunks != reference.chunks:
            raise AssertionError('Chunk order changed')
        np.testing.assert_allclose(current.vectors,reference.vectors,atol=3e-5,rtol=3e-5)
    timings = []
    for rep in range(args.repetitions):
        order = np.random.default_rng(20261022+rep).permutation(len(configurations))
        for index in order:
            batch, ordered = configurations[index]
            encoder.batch_size, encoder.sort_by_length = batch, ordered
            start = time.perf_counter()
            current = encoder.encode_documents(selected)
            wall = time.perf_counter()-start
            if current.chunks != reference.chunks:
                raise AssertionError('Chunk order changed')
            np.testing.assert_allclose(current.vectors,reference.vectors,atol=3e-5,rtol=3e-5)
            row = {'repetition':rep+1, **current.timings, 'caller_seconds':wall,
                   'max_abs_embedding_difference':float(np.max(np.abs(current.vectors-reference.vectors)))}
            timings.append(row)
            print(f'Measurement {rep+1}/{args.repetitions}: batch={batch}, sorted={ordered}, {wall:.3f}s; outputs PASS',flush=True)
            with (out/'timings.csv').open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=list(row));writer.writeheader();writer.writerows(timings)
    summary=[]
    for batch,ordered in configurations:
        rows=[r for r in timings if r['batch_size']==batch and r['sort_by_length']==ordered]
        seconds=statistics.median(r['caller_seconds'] for r in rows)
        summary.append({'batch_size':batch,'sort_by_length':ordered,'median_seconds':seconds,
                        'min_seconds':min(r['caller_seconds'] for r in rows),
                        'max_seconds':max(r['caller_seconds'] for r in rows),
                        'documents_per_second':len(selected)/seconds,'chunks_per_second':len(reference.chunks)/seconds,
                        'padding_fraction':1-rows[0]['tokens']/rows[0]['padded_tokens']})
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    source_paths = sorted([*ROOT.glob('src/eninca_documents/*.py'),*ROOT.glob('src/eninca_documents/*.json'),
                           ROOT/'benchmarks/run_public.py',*ROOT.glob('scripts/*.py')])
    report={'status':'pass','scope':'Public French guidance; CPU benchmark, not customer validation',
            'environment':provenance(),'encoder':encoder.identity,'tpu_tested':False,
            'corpus_checks':checks,'data_manifest_sha256':sha(data/'manifest.json'),
            'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in source_paths},
            'outputs_sha256':{name:sha(out/name) for name in ['calibration.json','quality.json','timings.csv']},
            'quality':quality,'model_setup_seconds':encoder.setup_seconds,
            'quality_encoding_timings':{k:v.timings for k,v in encoded.items()},
            'timing_document_ids':[d.id for d in selected], 'timing_documents':len(selected),
            'timing_chunks':len(reference.chunks),'repetitions':args.repetitions,'summary':summary,
            'process_peak_rss_bytes':rss if sys.platform=='darwin' else rss*1024,
            'memory_scope':'Cumulative process high-water mark, including model, warmups and retained quality/reference embeddings; not per-configuration memory.',
            'timing_scope':'Warm synchronous CPU encoding: tokenization, every overlapping chunk, inference, masked pooling and validation. Model setup, reads, exports and output comparisons excluded.',
            'limitations':['No TPU or GPU inference measured.', 'Timing repeats reuse identical documents; not independent quality observations.',
                           'Empirical validation precision target is not a test-set guarantee; rejection can leave zero accepted examples.',
                           'Wilson intervals are descriptive binomial approximations; related documents need not be independent.',
                           'Frozen public guidance is a domain proxy; no OCR, scans or private records.',
                           'Timing configuration search has no separate performance confirmation campaign.']}
    write_json(out/'report.json',report)
    print(json.dumps(summary,indent=2),flush=True)
    print('PASS: report saved to '+str(out/'report.json'),flush=True)


if __name__=='__main__':
    main()
