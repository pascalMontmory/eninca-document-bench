import tempfile
from pathlib import Path
import threading
import time
import unittest
from unittest.mock import patch

from demo.performance import ComparisonManager
from benchmarks.comparison import Cancelled


class ManagerContracts(unittest.TestCase):
    def test_single_run_cancellation_preserves_last_completed_evidence(self):
        class App:
            lock = threading.RLock()
            encoder = object()
        entered = threading.Event()

        def runner(encoder, output, *, progress, cancelled):
            entered.set()
            while not cancelled():
                time.sleep(.01)
            raise Cancelled()

        with tempfile.TemporaryDirectory() as tmp:
            app = App()
            app.state_dir = Path(tmp)
            manager = ComparisonManager(app)
            manager.record = {"prior": "unchanged"}
            with patch("demo.performance.run_comparison", runner):
                manager.start()
                self.assertTrue(entered.wait(3))
                with self.assertRaises(ValueError):
                    manager.start()
                manager.cancel()
                deadline = time.monotonic() + 3
                while manager.status()["running"] and time.monotonic() < deadline:
                    time.sleep(.01)
                self.assertFalse(manager.status()["running"])
            self.assertEqual(manager.status()["progress"]["phase"], "cancelled")
            self.assertEqual(manager.status()["report"], {"prior": "unchanged"})


if __name__ == "__main__":
    unittest.main()
