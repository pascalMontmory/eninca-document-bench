"""Compare archived Mac/VPS records without rerunning inference or changing thresholds."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
PATHS = {'vps': ROOT / 'results/public-cpu-20261022',
         'mac': ROOT / 'results/public-mac-20261022T110024Z'}
OUTPUT = ROOT / 'results/mac-vps-public-comparison-20261022.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a, b):
    if not math.isfinite(a) or not math.isfinite(b) or not math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError(f'Inconsistent recorded summary: {a}, {b}')


def load(directory):
    report = json.loads((directory / 'report.json').read_text())
    if report['status'] != 'pass' or report['tpu_tested'] is not False:
        raise ValueError('Expected a successful CPU run')
    for name, expected in report['outputs_sha256'].items():
        if sha(directory / name) != expected:
            raise ValueError('Output checksum mismatch: ' + name)
    with (directory / 'timings.csv').open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 6 * report['repetitions']:
        raise ValueError('Missing timing rows')
    summary = {}
    for item in report['summary']:
        key = (item['batch_size'], item['sort_by_length'])
        if key in summary:
            raise ValueError('Repeated configuration')
        selected = [r for r in rows if int(r['batch_size']) == key[0]
                    and r['sort_by_length'] == str(key[1])]
        if sorted(int(r['repetition']) for r in selected) != list(range(1, report['repetitions'] + 1)):
            raise ValueError('Missing or repeated measurement')
        seconds = [float(r['caller_seconds']) for r in selected]
        close(item['median_seconds'], statistics.median(seconds))
        close(item['min_seconds'], min(seconds))
        close(item['max_seconds'], max(seconds))
        close(item['documents_per_second'], report['timing_documents'] / statistics.median(seconds))
        close(item['chunks_per_second'], report['timing_chunks'] / statistics.median(seconds))
        summary[key] = item
    quality = json.loads((directory / 'quality.json').read_text())
    policy = json.loads((directory / 'calibration.json').read_text())
    return report, rows, summary, quality, policy


def compare():
    vps, mac = (load(PATHS[k]) for k in ['vps', 'mac'])
    equal_fields = ['source_sha256', 'encoder', 'data_manifest_sha256', 'timing_document_ids',
                    'timing_documents', 'timing_chunks', 'repetitions', 'quality', 'timing_scope']
    for field in equal_fields:
        if vps[0][field] != mac[0][field]:
            raise ValueError('Runs do not share ' + field)
    for field in ['mode', 'min_score', 'min_margin', 'selection_policy', 'validation_documents', 'validation_metrics']:
        if vps[4][field] != mac[4][field]:
            raise ValueError('Calibration policies differ: ' + field)
    decisions = {}
    for field in ['predictions', 'fixed_default_predictions']:
        a, b = vps[3][field], mac[3][field]
        if len(a) != len(b) or not a:
            raise ValueError('Different prediction counts')
        equal = sum(all(x[k] == y[k] for k in ['document_id', 'label', 'suggested_label', 'needs_review'])
                    for x, y in zip(a, b))
        decisions[field] = {'rows': len(a), 'identical_decisions': equal,
                           'max_abs_cosine_score_difference': max(abs(x['cosine_score'] - y['cosine_score']) for x,y in zip(a,b)),
                           'max_abs_margin_difference': max(abs(x['margin'] - y['margin']) for x,y in zip(a,b))}
        if equal != len(a):
            raise ValueError('Classification decisions differ')
    if set(vps[2]) != set(mac[2]):
        raise ValueError('Different measured configurations')
    configurations = []
    for key in sorted(vps[2]):
        a, b = vps[2][key], mac[2][key]
        configurations.append({'batch_size':key[0], 'sort_by_length':key[1],
            'vps_median_seconds':a['median_seconds'], 'mac_median_seconds':b['median_seconds'],
            'vps_documents_per_second':a['documents_per_second'], 'mac_documents_per_second':b['documents_per_second'],
            'mac_throughput_vs_vps_percent':100 * (a['median_seconds']/b['median_seconds'] - 1)})
    best_vps = min(vps[2].values(), key=lambda x:x['median_seconds'])
    best_mac = min(mac[2].values(), key=lambda x:x['median_seconds'])
    return {'schema':1, 'status':'pass', 'scope':'Offline comparison of archived runs; no new inference.',
            'comparison_script_sha256':sha(Path(__file__)),
            'inputs_sha256':{str(p.relative_to(ROOT)):sha(p) for d in PATHS.values()
                             for p in sorted(d.iterdir()) if p.suffix in {'.json','.csv'}},
            'identical_report_fields':equal_fields, 'decision_comparison':decisions,
            'configurations':configurations, 'best_observed':{'mac':best_mac, 'vps':best_vps},
            'best_mac_vs_best_vps_throughput_percent':100*(best_vps['median_seconds']/best_mac['median_seconds']-1),
            'mac_batch4_sorting_time_reduction_percent':100*(1-mac[2][4,True]['median_seconds']/mac[2][4,False]['median_seconds']),
            'environments':{key:{k:record[0]['environment'][k] for k in ['platform','machine','cpu_model','logical_cpus','python','packages']}
                            for key,record in [('vps',vps),('mac',mac)]},
            'threads':{key:sorted({int(r['threads']) for r in record[1]}) for key,record in [('vps',vps),('mac',mac)]},
            'process_peak_rss_bytes':{'vps':vps[0]['process_peak_rss_bytes'],'mac':mac[0]['process_peak_rss_bytes']},
            'limitations':['Raw embedding arrays were not archived; cross-machine bitwise embedding equality is not established.',
                           'Floating scores differ despite identical decisions on these 80 documents under both policies.',
                           'The 90% validation precision target remains unmet on test: 27/33 accepted decisions are correct.',
                           'Python, NumPy, OS, hardware and machine load differ; this is not an architecture-only experiment.',
                           'Three warm repetitions; best observed configurations have no separate confirmation campaign.',
                           'Public text workload on CPU only; no GPU/TPU or customer performance claim.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Create a new comparison record; never overwrite')
    args = parser.parse_args()
    result = compare()
    if args.write:
        with OUTPUT.open('x') as stream:
            json.dump(result, stream, indent=2, allow_nan=False)
            stream.write('\n')
    elif json.loads(OUTPUT.read_text()) != result:
        raise ValueError('Comparison record differs from recomputed evidence')
    print(json.dumps({'status':'pass', 'compared_timing_rows':36,
                      'classification':result['decision_comparison'], 'record':str(OUTPUT.relative_to(ROOT))}, indent=2))


if __name__ == '__main__':
    main()
