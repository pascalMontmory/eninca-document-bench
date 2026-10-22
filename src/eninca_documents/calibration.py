"""Validation-only threshold selection for assisted classification, not probabilities."""
import hashlib
import json
import math
import unicodedata

import numpy as np

from .core import text_sha256


def canonical_hash(text):
    return text_sha256(' '.join(unicodedata.normalize('NFKC', text).casefold().split()))


def classifier_fingerprint(classifier):
    contract = json.dumps({'encoder': classifier.encoder_identity, 'labels': classifier.labels},
                          sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(contract + classifier.centroids.astype('<f4').tobytes()).hexdigest()


def wilson(correct, total):
    if not total:
        return None
    z = 1.959963984540054
    p = correct / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [max(0., centre - radius), min(1., centre + radius)]


def decision_metrics(documents, predictions, known_labels):
    if not documents or len(documents) != len(predictions):
        raise ValueError('Nonempty aligned evaluation required')
    if any(d.label is None or d.id != p['document_id'] for d, p in zip(documents, predictions)):
        raise ValueError('Labeled documents in prediction order required')
    known = set(known_labels)
    if any(p['label'] is not None and p['label'] not in known for p in predictions):
        raise ValueError('Prediction outside trained labels')
    accepted = correct = known_count = known_accepted = unknown = unknown_accepted = 0
    for doc, pred in zip(documents, predictions):
        is_known = doc.label in known
        is_accepted = pred['label'] is not None
        known_count += is_known
        known_accepted += is_known and is_accepted
        unknown += not is_known
        unknown_accepted += not is_known and is_accepted
        accepted += is_accepted
        correct += is_known and is_accepted and pred['label'] == doc.label
    return dict(documents=len(documents), known_documents=known_count, unknown_documents=unknown,
                accepted=accepted, correct_accepted=correct, incorrect_accepted=accepted-correct,
                coverage=accepted/len(documents),
                known_coverage=known_accepted/known_count if known_count else None,
                accepted_precision=correct/accepted if accepted else None,
                accepted_precision_wilson95=wilson(correct, accepted),
                known_accuracy_counting_abstentions_as_errors=correct/known_count if known_count else None,
                unknown_false_accepts=unknown_accepted,
                unknown_false_accept_rate=unknown_accepted/unknown if unknown else None,
                unknown_false_accept_wilson95=wilson(unknown_accepted,unknown))


def _apply(raw, mode, score, margin):
    result = []
    for row in raw:
        accepted = mode == 'thresholds' and row['cosine_score'] >= score and row['margin'] >= margin
        result.append({**row, 'label': row['suggested_label'] if accepted else None,
                       'needs_review': not accepted})
    return result


def calibrate(classifier, validation, *, target_precision=.90, minimum_accepted=5):
    if not 0 < target_precision <= 1 or minimum_accepted < 1:
        raise ValueError('Invalid calibration objective')
    raw = classifier.predict(validation, min_score=-1, min_margin=0)
    if not any(d.label not in classifier.labels for d in validation.documents):
        raise ValueError('Include labeled out-of-scope validation examples')
    candidates = []
    for score in np.linspace(0, .95, 39):
        for margin in np.linspace(0, .30, 31):
            metrics = decision_metrics(validation.documents, _apply(raw, 'thresholds', score, margin), classifier.labels)
            if metrics['accepted'] >= minimum_accepted and metrics['accepted_precision'] >= target_precision:
                # Maximize accepted known documents, then precision, then stricter thresholds.
                candidates.append(((metrics['known_coverage'], metrics['accepted_precision'], float(score), float(margin)), metrics))
    if candidates:
        (_, _, score, margin), metrics = max(candidates, key=lambda c:c[0])
        mode = 'thresholds'
    else:
        mode, score, margin = 'reject_all', None, None
        metrics = decision_metrics(validation.documents, _apply(raw, mode, score, margin), classifier.labels)
    return dict(schema=1, classifier_sha256=classifier_fingerprint(classifier), mode=mode,
                min_score=score, min_margin=margin,
                selection_policy={'target_empirical_precision':target_precision, 'minimum_accepted':minimum_accepted,
                                  'score_grid':[0.,.95,39], 'margin_grid':[0.,.30,31],
                                  'objective':'known coverage, precision, stricter thresholds'},
                validation_documents=[{'id':d.id, 'canonical_sha256':canonical_hash(d.text)} for d in validation.documents],
                validation_metrics=metrics,
                limitation='Selected on validation only; this target and its interval are not a test-set guarantee.')


def predict_calibrated(classifier, corpus, calibration):
    if calibration.get('schema') != 1 or calibration.get('classifier_sha256') != classifier_fingerprint(classifier):
        raise ValueError('Calibration does not match this classifier and encoder')
    mode = calibration.get('mode')
    score, margin = calibration.get('min_score'), calibration.get('min_margin')
    if mode not in {'thresholds', 'reject_all'}:
        raise ValueError('Invalid calibration mode')
    if mode == 'thresholds' and (not isinstance(score,(float,int)) or not isinstance(margin,(float,int))
                                 or not 0 <= score <= 1 or not 0 <= margin <= 2):
        raise ValueError('Invalid calibration thresholds')
    used_ids = {r['id'] for r in calibration['validation_documents']}
    used_hashes = {r['canonical_sha256'] for r in calibration['validation_documents']}
    if used_ids & {d.id for d in corpus.documents} or used_hashes & {canonical_hash(d.text) for d in corpus.documents}:
        raise ValueError('Validation/test leakage')
    return _apply(classifier.predict(corpus, min_score=-1, min_margin=0), mode, score, margin)
