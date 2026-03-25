import requests
import os
try:
    from playwright.sync_api import sync_playwright
    _HAS_PLAYWRIGHT = True
except Exception:
    _HAS_PLAYWRIGHT = False

PAGE_FILE = "page.html"
ENCODING = "utf-8"


class SimpleResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code


def download_page_js(url, timeout=30000) -> SimpleResponse:
    """Fetch page using Playwright (headless browser) and return an object
    with `.text` and `.status_code` similar to `requests.Response`.
    """
    if not _HAS_PLAYWRIGHT:
        raise RuntimeError("Playwright is not installed. Install with `pip install playwright` and run `playwright install`.")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=timeout)
        content = page.content()
        browser.close()
    return SimpleResponse(content, 200)


def download_page(url):
    """
    Stáhne stránku zadaného URL a vrátí její obsah.

    Uses a lightweight `requests.get` first. If the returned HTML contains
    a JavaScript-required notice (e.g. Datoid "Zapněte si prosím Javascript"),
    falls back to Playwright to render the page and returns the rendered HTML.
    """
    response = requests.get(url)
    """
    text = response.text if response is not None else ""

    js_signals = (
        "Zapněte si prosím Javascript",
        "mít zapnutý Javascript",
        "Please enable JavaScript",
        "enable JavaScript",
    )
    if any(sig in text for sig in js_signals):
        if _HAS_PLAYWRIGHT:
            return download_page_js(url)
        else:
            # return original response but caller can detect JS requirement via text
            return response
    """
    return response

def save_binary_file(response, file_path):
    """
    Uloží data do binárního souboru.
    """
    with open(file_path, "wb") as file:
        file.write(response.content)

def download_and_save_page(url, file_name=PAGE_FILE):
    page = requests.get(url)
    with open(file_name, "w", encoding=ENCODING) as file:
        file.write(page.text)

def load_page_from_file(file_name=PAGE_FILE):
    class Dumy:
        text = ""
    page = Dumy()
    with open(file_name, "r", encoding=ENCODING) as file_name:
        page.text = file_name.read()
    return page