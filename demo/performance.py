"""One serialized, cancellable comparison at a time; last complete evidence survives failures."""
import io
from pathlib import Path
import threading
import time
import traceback
from uuid import uuid4
import zipfile

from benchmarks.comparison import Cancelled, run_comparison, verify_report

ROOT = Path(__file__).resolve().parents[1]


class ComparisonManager:
    def __init__(self, app):
        self.app = app
        self.lock = threading.Lock()
        self.cancel_event = threading.Event()
        self.running = False
        self.progress = dict(phase="idle", completed=0, total=20)
        self.record = self.record_directory = self.source = None
        self.load_error = False
        local = app.state_dir / "comparisons"
        candidates = sorted(local.glob("*/report.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        candidates += [ROOT / "results/index-comparison-20261022/report.json"]
        for path in candidates:
            if path.is_file():
                try:
                    self.record = verify_report(path.parent)
                    self.record_directory = path.parent
                    self.source = "archived" if path.is_relative_to(ROOT / "results") else "local"
                    break
                except (ValueError, OSError, KeyError):
                    self.load_error = True

    def status(self):
        with self.lock:
            return dict(running=self.running, progress=dict(self.progress), report=self.record,
                        source=self.source, load_error=self.load_error, cancel_requested=self.cancel_event.is_set())

    def start(self):
        with self.lock:
            if self.running:
                raise ValueError("benchmark_busy")
            self.running = True
            self.cancel_event.clear()
            self.progress = dict(phase="starting", completed=0, total=20)
            self.started = time.perf_counter()
        threading.Thread(target=self._run, daemon=True).start()

    def cancel(self):
        with self.lock:
            if self.running:
                self.cancel_event.set()

    def _progress(self, value):
        with self.lock:
            self.progress = value

    def _run(self):
        from datetime import datetime, timezone
        name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
        out = self.app.state_dir / "comparisons" / name
        try:
            # Reuse the single loaded model, avoiding a second gigabyte-sized session.
            # Other inference/review actions are rejected by HTTP while this lock is held.
            with self.app.lock:
                run_comparison(self.app.encoder, out, progress=self._progress, cancelled=self.cancel_event.is_set)
                report = verify_report(out)
            with self.lock:
                self.record, self.record_directory, self.source = report, out, "local"
        except Cancelled:
            self._progress(dict(phase="cancelled", completed=0, total=20))
        except Exception:
            traceback.print_exc()
            self._progress(dict(phase="failed", completed=0, total=20))
        finally:
            with self.lock:
                self.running = False

    def download(self, kind):
        with self.lock:
            directory = self.record_directory
        if directory is None:
            raise ValueError("No completed report")
        verify_report(directory)
        if kind in {"json", "csv"}:
            path = directory / ("report.json" if kind == "json" else "timings.csv")
            return path.read_bytes(), "application/json" if kind == "json" else "text/csv", "eninca-comparison." + kind
        if kind != "zip":
            raise ValueError("Invalid download type")
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            for name in ("report.json", "plan.json", "timings.csv", "calibration.json", "predictions.json"):
                if (directory / name).is_file():
                    archive.write(directory / name, name)
        return buffer.getvalue(), "application/zip", "eninca-comparison.zip"
