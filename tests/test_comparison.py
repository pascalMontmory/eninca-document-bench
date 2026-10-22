import copy
import tempfile
from pathlib import Path
import unittest

import numpy as np

from benchmarks.comparison import paired_summary, run_comparison, verify_report
from eninca_documents.core import Corpus, Chunk


class ComparisonContracts(unittest.TestCase):
    def test_paired_uncertainty_does_not_force_a_winner(self):
        def rows(ratios):
            return [dict(pair=i, variant=v, index_seconds=10 if v == "reference" else 10/r)
                    for i, r in enumerate(ratios, 1) for v in ("reference", "length_grouped")]
        self.assertEqual(paired_summary(rows([1.2]*7))["verdict"], "observed_gain")
        self.assertEqual(paired_summary(rows([.8]*7))["verdict"], "observed_regression")
        result = paired_summary(rows([.8, .9, .95, 1., 1.05, 1.1, 1.2]))
        self.assertEqual(result["verdict"], "inconclusive")
        self.assertAlmostEqual(result["median_paired_time_reduction_pct"], 0.)
        for invalid in [rows([1, 1]), rows([1, 1, 1])[:-1], rows([1, 1, 1])+rows([1])]:
            with self.assertRaises(ValueError):
                paired_summary(invalid)

    def test_local_campaign_records_comparable_outputs_and_detects_tampering(self):
        class Encoder:
            batch_size, sort_by_length, threads = 8, True, 2
            identity = {"test_only": True}

            def encode_documents(self, docs):
                vectors = np.array([[1., len(d.text)/100] for d in docs], dtype=np.float32)
                chunks = [Chunk(d.id, 0, 0, len(d.text), 4) for d in docs]
                return Corpus(docs, chunks, vectors, self.identity,
                              dict(encode_seconds=.00001, tokens=4*len(docs), padded_tokens=5*len(docs)))

        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)/"input.jsonl"
            data.write_text(''.join('{"id":"d'+str(i)+'","text":"sample '+str(i)+'"}\n' for i in range(6)))
            out, encoder = Path(tmp)/"result", Encoder()
            progress = []
            report = run_comparison(encoder, out, input_path=data, repetitions=3, count=6, progress=progress.append)
            self.assertEqual(report["quality"]["status"], "not_evaluated")
            self.assertEqual(report["repetitions"], 3)
            self.assertEqual(report, verify_report(out))
            self.assertEqual((encoder.batch_size, encoder.sort_by_length), (8, True))
            self.assertEqual(progress[-1]["completed"], progress[-1]["total"])
            self.assertFalse(list(out.glob("working-*")))
            (out/"timings.csv").write_text("corrupted")
            with self.assertRaisesRegex(ValueError, "checksum"):
                verify_report(out)

    def test_cancel_restores_settings_and_does_not_publish_result(self):
        class Encoder:
            batch_size, sort_by_length = 8, True
        with tempfile.TemporaryDirectory() as tmp:
            from benchmarks.comparison import Cancelled
            out, encoder = Path(tmp)/"result", Encoder()
            with self.assertRaises(Cancelled):
                run_comparison(encoder, out, cancelled=lambda: True)
            self.assertEqual((encoder.batch_size, encoder.sort_by_length), (8, True))
            self.assertTrue((out/"failure.json").exists())
            self.assertFalse((out/"report.json").exists())


if __name__ == "__main__":
    unittest.main()
