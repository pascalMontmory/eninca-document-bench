import copy
import unittest
import numpy as np

from eninca_documents.core import Corpus, Document, Chunk, PrototypeClassifier
from eninca_documents.calibration import calibrate, predict_calibrated, decision_metrics


def corpus(rows):
    docs=[Document(i,text,label) for i,text,label,vector in rows]
    return Corpus(
        docs,[Chunk(d.id,0,0,len(d.text),1) for d in docs],np.array([r[3] for r in rows]),{'model':'fixture'})


class CalibrationContracts(unittest.TestCase):
    def setUp(self):
        self.classifier=PrototypeClassifier(corpus([('ta','training A','a',[1.,0.]),('tb','training B','b',[0.,1.])]))
        self.validation=corpus([('va','validation A','a',[1.,0.]),('vb','validation B','b',[0.,1.]),
                                ('vu','Unknown topic','outside',[.7,.7])])

    def test_unknown_rejection_and_held_out_prediction(self):
        policy=calibrate(self.classifier,self.validation,minimum_accepted=2)
        test=corpus([('ea','evaluation A','a',[1.,0.]),('eu','unseen unknown','outside',[.7,.7])])
        predictions=predict_calibrated(self.classifier,test,policy)
        self.assertEqual([p['label'] for p in predictions],['a',None])
        metrics=decision_metrics(test.documents,predictions,self.classifier.labels)
        self.assertEqual(metrics['unknown_false_accept_rate'],0.)

    def test_validation_leakage_and_classifier_change_are_rejected(self):
        policy=calibrate(self.classifier,self.validation,minimum_accepted=2)
        with self.assertRaisesRegex(ValueError,'leakage'):
            predict_calibrated(self.classifier,self.validation,policy)
        duplicate=corpus([('newid','  UNKNOWN   topic ','outside',[.7,.7])])
        with self.assertRaisesRegex(ValueError,'leakage'):
            predict_calibrated(self.classifier,duplicate,policy)
        changed=copy.deepcopy(self.classifier);changed.centroids[0,0]=.5
        with self.assertRaisesRegex(ValueError,'match'):
            predict_calibrated(changed,duplicate,policy)

    def test_infeasible_target_rejects_all_without_claiming_accuracy(self):
        policy=calibrate(self.classifier,self.validation,minimum_accepted=4)
        self.assertEqual(policy['mode'],'reject_all')
        self.assertIsNone(policy['validation_metrics']['accepted_precision'])
        self.assertIsNone(policy['validation_metrics']['accepted_precision_wilson95'])

    def test_unknown_false_accept_is_not_a_correct_prediction(self):
        test=corpus([('u','Unrelated topic','outside',[1.,0.])])
        metrics=decision_metrics(test.documents,self.classifier.predict(test),self.classifier.labels)
        self.assertEqual(metrics['accepted_precision'],0.)
        self.assertEqual(metrics['unknown_false_accept_rate'],1.)

    def test_calibration_requires_unknown_examples_and_valid_parameters(self):
        known=corpus([('k','known topic','a',[1.,0.])])
        with self.assertRaisesRegex(ValueError,'out-of-scope'):
            calibrate(self.classifier,known)
        with self.assertRaises(ValueError):
            calibrate(self.classifier,self.validation,target_precision=1.1)


if __name__=='__main__':
    unittest.main()
