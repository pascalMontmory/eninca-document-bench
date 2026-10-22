"""Optional browser check of real comparison evidence and start/cancel controls."""
import argparse
import csv
import io
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
import zipfile

from playwright.sync_api import expect, sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8765")
    parser.add_argument("--out", required=True)
    parser.add_argument("--browser-executable")
    parser.add_argument("--check-cancel", action="store_true", help="Start and cancel an actual native run")
    args = parser.parse_args()
    parsed = urlsplit(args.url)
    if parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or parsed.path not in ("", "/"):
        parser.error("Use a loopback demo URL")
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=False)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.browser_executable)
        context = browser.new_context(viewport={"width": 1440, "height": 1050}, accept_downloads=True)
        page = context.new_page()
        errors, requests = [], []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("request", lambda req: requests.append(req.url))
        page.goto(args.url)
        page.locator("#application").wait_for(state="visible", timeout=300_000)
        expect(page.locator("#performance-view")).to_be_visible()
        expect(page.locator("#benchmark-result")).to_be_visible()
        current = context.request.get(args.url + "/api/benchmark/status").json()
        if current["running"]:
            expect(page.locator("#benchmark-start")).to_be_disabled()
            if args.check_cancel:
                raise RuntimeError("A comparison is already running; do not interrupt it")
        else:
            expect(page.locator("#benchmark-start")).to_be_enabled()
        original = current["report"]
        assert original and original["status"] == "pass"
        expect(page.locator("#comparison-values tr")).to_have_count(7)
        page.screenshot(path=str(output / "comparison-fr.png"), full_page=True)
        page.locator("#language").select_option("en")
        assert "€" not in page.locator("#cost-output").inner_text()
        for index, variant in enumerate(("reference", "length_grouped")):
            text = page.locator("#comparison-values tr").first.locator("td").nth(index).inner_text()
            assert abs(float(text.removesuffix(" s")) - original["variants"][variant]["median_index_seconds"]) < .00051
        page.locator("#hourly-rate").fill("2")
        page.locator("#cost-volume").fill("1000")
        values = page.locator("#cost-output dd").all_inner_texts()
        actual = [float(re.sub(r"[^0-9.\-]", "", v)) for v in values]
        expected = [original["variants"][v]["median_index_seconds"]/original["documents"]*1000/3600*2
                    for v in ("reference", "length_grouped")]
        expected.append(expected[0]-expected[1])
        assert len(actual) == 3 and all(abs(a-b) < .000051 for a, b in zip(actual, expected))
        for kind, selector in (("csv", "downloadTimings"), ("zip", "downloadEvidence")):
            with page.expect_download() as pending:
                page.locator(f'[data-t="{selector}"]').click()
            pending.value.save_as(output / ("evidence." + kind))
        assert len(list(csv.DictReader(io.StringIO((output / "evidence.csv").read_text())))) == 2*original["repetitions"]
        with zipfile.ZipFile(output / "evidence.zip") as archive:
            assert json.loads(archive.read("report.json")) == original
        page.set_viewport_size({"width": 390, "height": 844})
        page.screenshot(path=str(output / "comparison-mobile-en.png"), full_page=True)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        if args.check_cancel:
            page.locator("#benchmark-start").click()
            expect(page.locator("#benchmark-progress-box")).to_be_visible()
            expect(page.locator('[data-view="search"]')).to_be_disabled()
            page.locator("#benchmark-cancel").click()
            expect(page.locator("#benchmark-start")).to_be_enabled(timeout=60_000)
            result = context.request.get(args.url + "/api/benchmark/status").json()
            assert not result["running"] and result["progress"]["phase"] == "cancelled"
            assert result["report"] == original
            expect(page.locator('[data-view="search"]')).to_be_enabled()
            page.reload()
            expect(page.locator("#benchmark-result")).to_be_visible()
            page.locator('[data-view="summary"]').click()
            expect(page.locator("#summary-cards .card")).to_have_count(4)
        assert not errors, errors
        assert all(url.startswith(args.url + "/") for url in requests), requests
        report = dict(status="pass", checks=["first_view_comparison", "raw_medians_displayed", "conditional_cost_arithmetic",
                    "csv_and_zip_downloads", "french_and_english", "mobile_no_horizontal_overflow", "no_external_requests"],
                      native_start_cancel=args.check_cancel, measured_verdict=original["comparison"]["verdict"],
                      limitation="Functional browser check; timings remain those in the independent native campaign.")
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        browser.close()


if __name__ == "__main__":
    main()
