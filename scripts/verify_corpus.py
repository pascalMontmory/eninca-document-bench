"""Check frozen public data, source extraction and group-level split isolation."""
import hashlib
import json
from pathlib import Path
import zipfile

from prepare_public_corpus import extract, shingles

ROOT = Path(__file__).resolve().parents[1]


def verify(directory):
    manifest = json.loads((directory / 'manifest.json').read_text())
    for name, expected in manifest['files'].items():
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Corpus checksum mismatch: {name}')
    rows = {r['id']:r for r in manifest['documents']}
    seen_ids, seen_texts, groups, allgrams = set(), set(), {}, []
    with zipfile.ZipFile(directory / 'source-xml.zip') as z:
        for split in ['train','validation','test']:
            for line in (directory / (split + '.jsonl')).read_text().splitlines():
                doc = json.loads(line)
                entry = rows[doc['id']]
                source = extract(z.read(doc['id'] + '.xml'))
                if entry['split'] != split or any(source[k] != doc[k] for k in doc):
                    raise ValueError('Source extraction or split mismatch')
                if source['xml_sha256'] != entry['xml_sha256']:
                    raise ValueError('Source checksum mismatch')
                digest = hashlib.sha256(doc['text'].encode()).hexdigest()
                if digest != entry['text_sha256'] or doc['id'] in seen_ids or digest in seen_texts:
                    raise ValueError('Duplicate document or content mismatch')
                seen_ids.add(doc['id']); seen_texts.add(digest)
                group = entry['group']
                if group in groups and groups[group] != split:
                    raise ValueError('Dossier family crosses splits')
                groups[group] = split
                grams = shingles(doc['text'])
                if any(len(grams & other)/len(grams | other) >= .70 for other in allgrams):
                    raise ValueError('Near duplicate')
                allgrams.append(grams)
                if split == 'train' and doc['label'] not in manifest['known_labels']:
                    raise ValueError('Unknown topic in training')
    if seen_ids != set(rows):
        raise ValueError('Missing documents')
    return {'documents':len(rows), 'families':len(groups), 'source_and_split_checks':'pass'}


if __name__ == '__main__':
    print(json.dumps(verify(ROOT / 'data/dila-v1')))
