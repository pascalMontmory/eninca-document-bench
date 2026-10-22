"""Optional browser smoke check, using a running local demo and Playwright.

Uses the real model through the server. Adds a decision, checks the export,
then restores that document's prior decision. Does not measure retrieval quality.
Screenshots and diagnostics go into a new local directory.
"""
import argparse
import csv
import io
import json
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8765")
    parser.add_argument("--out", required=True)
    parser.add_argument("--browser-executable", help="Optional existing Chromium executable")
    args = parser.parse_args()
    parsed = urlsplit(args.url)
    if parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or parsed.path not in ("", "/"):
        parser.error("A loopback HTTP demo URL is required")
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=False)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.browser_executable)
        context = browser.new_context(viewport={"width": 1440, "height": 1050}, accept_downloads=True)
        page = context.new_page()
        errors, requests = [], []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.on("request", lambda request: requests.append(request.url))
        page.goto(args.url)
        page.locator("#application").wait_for(state="visible", timeout=300_000)
        before = context.request.get(args.url + "/api/state").json()
        assert before["documents"] == 220 and len(before["rows"]) == 80
        page.locator('[data-view="search"]').click()
        page.locator('[data-t="example1"]').click()
        expect(page.locator(".result")).to_have_count(5)
        expect(page.locator("#search-submit")).to_be_enabled()
        page.screenshot(path=str(output / "search-desktop.png"), full_page=True)
        page.locator(".result button").first.click()
        page.locator("#document-dialog").wait_for(state="visible")
        assert len(page.locator("#document-text").inner_text()) > 500
        page.locator("#close-dialog").click()
        page.locator('[data-view="review"]').click()
        page.locator("#review-filter").select_option("abstained")
        candidates = [r for r in before["rows"] if r["needs_review"] and r["review"]["label"] is None]
        assert candidates, "Use a demo directory with at least one unreviewed abstention"
        chosen = candidates[0]
        page.locator("#decision").select_option("out_of_scope")
        page.get_by_role("button", name="Enregistrer ma décision", exact=True).click()
        page.get_by_role("status").filter(has_text="Décision enregistrée localement.").wait_for(state="visible")
        after = context.request.get(args.url + "/api/state").json()
        assert after["metrics"] == before["metrics"]
        assert after["review_counts"]["completed"] == before["review_counts"]["completed"] + 1
        saved = next(r for r in after["rows"] if r["document_id"] == chosen["document_id"])
        assert saved["review"]["label"] == "out_of_scope"
        page.locator("#review-filter").select_option("done")
        page.screenshot(path=str(output / "review-desktop.png"), full_page=True)
        page.locator('[data-view="summary"]').click()
        page.screenshot(path=str(output / "summary-desktop.png"), full_page=True)
        with page.expect_download() as pending:
            page.locator('[data-t="export"]').click()
        download = pending.value
        download.save_as(output / "decisions.csv")
        exported = list(csv.DictReader(io.StringIO((output / "decisions.csv").read_text(encoding="utf-8-sig"))))
        assert len(exported) == 80
        assert next(r for r in exported if r["document_id"] == chosen["document_id"])["human_label"] == "out_of_scope"
        token = context.request.get(args.url + "/api/status").json()["token"]
        response = context.request.post(args.url + "/api/review", data=dict(document_id=chosen["document_id"], label=None,
                                         revision=saved["review"]["revision"]), headers={"X-Demo-Token": token})
        assert response.ok
        await_undo = context.request.get(args.url + "/api/state").json()
        assert await_undo["review_counts"] == before["review_counts"]
        # Refresh visible state after the direct API undo, as a real navigation does.
        page.locator('[data-view="summary"]').click()
        page.locator("#language").select_option("en")
        page.get_by_role("heading", name="A summary you can check.").wait_for(state="visible")
        page.locator("#toast").wait_for(state="hidden")
        page.set_viewport_size({"width": 390, "height": 844})
        page.screenshot(path=str(output / "summary-mobile-en.png"), full_page=True)
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.locator('[data-view="search"]').click()
        page.locator("#query").fill("word " * 300)
        page.locator("#search-submit").click()
        page.locator("#error").wait_for(state="visible")
        assert "shorter question" in page.locator("#error").inner_text()
        # The intentionally rejected overlong query is a normal HTTP 400.
        errors = [e for e in errors if "400 (Bad Request)" not in e]
        assert not errors, errors
        assert all(url.startswith(args.url + "/") for url in requests), requests
        report = dict(status="pass", documents=220, review_documents=80,
                      checks=["search_and_original_text", "human_review", "unchanged_model_metrics", "csv_export", "undo",
                              "french_and_english", "mobile_no_horizontal_overflow", "long_query_rejected", "no_external_requests"],
                      model_metrics=before["metrics"], scope=before["scope"],
                      limitation="Functional browser check on CPU, not a retrieval-quality or performance benchmark.")
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        browser.close()


if __name__ == "__main__":
    main()
