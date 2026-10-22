"""Build a small, frozen, attributed DILA benchmark. No model or scores involved."""
import argparse
import collections
import datetime
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

DC = '{http://purl.org/dc/elements/1.1/}'
KNOWN = ['N19803', 'N19806', 'N19808', 'N19811']
UNKNOWN = ['N19810', 'N19812']
URL = 'https://lecomarquage.service-public.gouv.fr/vdd/3.5/part/zip/vosdroits-latest.zip'
ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def rank(value):
    return digest(('eninca-documents-v1:' + value).encode())


def shingles(text):
    words = re.findall(r'\w+', text.casefold())
    return {tuple(words[i:i + 5]) for i in range(len(words) - 4)}


def extract(raw):
    root = ET.fromstring(raw)
    theme, family = root.find('Theme'), root.find('DossierPere')
    if theme is None or family is None:
        return None
    parts = [root.findtext(DC + 'title', '')]
    # Do not encode theme labels, breadcrumbs, related documents or legal footers.
    for section in root:
        if section.tag in {'Introduction', 'Texte', 'ListeSituations', 'Conclusion'}:
            for parent in section.iter():
                for child in list(parent):
                    if child.tag in {'Condition', 'TitreRiche'}:
                        parent.remove(child)
            parts.append(' '.join(section.itertext()))
    text = '\n\n'.join(re.sub(r'\s+', ' ', part).strip() for part in parts if part.strip())
    if not 500 <= len(text) <= 12000:
        return None  # selection filter, never silent truncation
    return dict(id=root.get('ID'), text=text, label=theme.get('ID'),
                theme=theme.findtext('Titre'), group=family.get('ID'),
                title=root.findtext(DC + 'title'), source_url=root.get('spUrl'),
                source_modified=root.findtext(DC + 'date'), xml_sha256=digest(raw))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', required=True)
    parser.add_argument('--out', default=str(ROOT / 'data/dila-v1'))
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    archive = Path(args.archive)
    candidates = []
    with zipfile.ZipFile(archive) as z:
        for name in sorted(z.namelist()):
            if re.fullmatch(r'F\d+\.xml', name):
                row = extract(z.read(name))
                if row and row['label'] in KNOWN + UNKNOWN:
                    candidates.append(row)
        assignments = {}
        for label in KNOWN + UNKNOWN:
            groups = sorted({r['group'] for r in candidates if r['label'] == label}, key=rank)
            names = ['train', 'validation', 'test'] if label in KNOWN else ['validation', 'test']
            for i, group in enumerate(groups):
                assignments[(label, group)] = names[i % len(names)]
        selected, seen, counts = [], [], collections.Counter()
        for row in sorted(candidates, key=lambda r: rank(r['id'])):
            split = assignments[row['label'], row['group']]
            key = (row['label'], split)
            limit = 15 if row['label'] in KNOWN else 10
            if counts[key] >= limit:
                continue
            grams = shingles(row['text'])
            if any(len(grams & other) / len(grams | other) >= .70 for other in seen):
                continue
            row['split'] = split
            row['text_sha256'] = digest(row['text'].encode())
            selected.append(row)
            seen.append(grams)
            counts[key] += 1
        expected = {(label, split): 15 for label in KNOWN for split in ['train', 'validation', 'test']}
        expected.update({(label, split): 10 for label in UNKNOWN for split in ['validation', 'test']})
        if dict(counts) != expected:
            raise ValueError(f'Insufficient independent groups: {counts}')
        for split in ['train', 'validation', 'test']:
            with (out / (split + '.jsonl')).open('x', encoding='utf-8') as f:
                for row in sorted(selected, key=lambda r: r['id']):
                    if row['split'] == split:
                        f.write(json.dumps({k: row[k] for k in ['id', 'text', 'label']}, ensure_ascii=False) + '\n')
        with zipfile.ZipFile(out / 'source-xml.zip', 'w', compression=zipfile.ZIP_DEFLATED) as dest:
            for row in sorted(selected, key=lambda r: r['id']):
                info = zipfile.ZipInfo(row['id'] + '.xml', date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                dest.writestr(info, z.read(row['id'] + '.xml'))
    manifest = dict(schema=1, source='Service Public / DILA', source_url=URL,
                    source_dataset='https://www.data.gouv.fr/fr/datasets/service-public-fr-guide-vos-droits-et-demarches-particuliers',
                    license='Licence Ouverte / Open Licence (data.gouv.fr identifier fr-lo)',
                    license_source='https://www.service-public.gouv.fr/P10004',
                    retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    upstream_archive_sha256=digest(archive.read_bytes()),
                    preparation_script_sha256=digest(Path(__file__).read_bytes()),
                    known_labels=KNOWN, out_of_scope_labels=UNKNOWN,
                    selection='SHA256 order; 500..12000 Unicode characters; no truncation; no model selection',
                    grouping='DILA parent dossier allocated per theme before document selection; no group crosses splits',
                    near_duplicate_filter='Word 5-gram Jaccard >= 0.70 rejected across all selected documents',
                    limitations=['Public guidance, not customer scans, invoices or production document types.',
                                 'Themes are editorial labels; plausible secondary themes can count as errors.',
                                 'Group separation and lexical filtering do not rule out all semantic overlap.',
                                 'Unknown topics are a proxy, not a guarantee of out-of-distribution detection.'],
                    files={p.name: digest(p.read_bytes()) for p in sorted(out.iterdir())},
                    documents=[{k: v for k, v in r.items() if k != 'text'} for r in sorted(selected, key=lambda r:r['id'])])
    (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'documents':len(selected), 'counts': {str(k): v for k,v in sorted(counts.items())}}, indent=2))


if __name__ == '__main__':
    main()
