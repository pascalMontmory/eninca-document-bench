"""Local pilot: training prototypes, separate validation, then a new unlabeled batch."""
import argparse
from pathlib import Path

from eninca_documents.core import read_jsonl, PrototypeClassifier
from eninca_documents.calibration import canonical_hash, calibrate, predict_calibrated
from eninca_documents.encoder import OnnxEncoder
from eninca_documents.cli import write_json


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for flag in ['model-dir','training','validation','input','out']:
        parser.add_argument('--'+flag, required=True)
    parser.add_argument('--threads', type=int, default=2)
    args=parser.parse_args()
    out=Path(args.out)
    if out.exists():
        raise ValueError('Output directory already exists')
    sets={name:read_jsonl(getattr(args,name)) for name in ['training','validation','input']}
    ids, hashes=set(),set()
    for name,documents in sets.items():
        current_ids={d.id for d in documents};current_hashes={canonical_hash(d.text) for d in documents}
        if ids & current_ids or hashes & current_hashes:
            raise ValueError('Training/validation/input overlap by id or normalized text')
        if len(current_hashes) != len(documents):
            raise ValueError('Repeated normalized text in '+name)
        ids.update(current_ids);hashes.update(current_hashes)
    encoder=OnnxEncoder(args.model_dir,threads=args.threads)
    classifier=PrototypeClassifier(encoder.encode_documents(sets['training']))
    policy=calibrate(classifier,encoder.encode_documents(sets['validation']))
    predictions=predict_calibrated(classifier,encoder.encode_documents(sets['input']),policy)
    out.mkdir(parents=True,exist_ok=False)
    write_json(out/'calibration.json',policy)
    write_json(out/'predictions.json',{'encoder':encoder.identity,'predictions':predictions,
               'scope':'Assisted classification; scores are not probabilities; human review remains required.'})
    print(f'{len(predictions)} documents; {sum(p["needs_review"] for p in predictions)} require review. Results: {out}')


if __name__=='__main__':
    main()
