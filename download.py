import requests


PAGE_FILE = "page.html"
ENCODING="utf-8"

def download_page(url):
    """
    Stáhne stránku zadaného URL a vrátí její obsah.
    """
    response = requests.get(url)
    return response

def save_binary_file(response, file_path):
    """
    Stáhne soubor z internetu a uloží jej do souboru.
    """
    with open(file_path, "wb") as file:
        file.write(response.content)

def download_and_save_page(url, file_name=PAGE_FILE):
    page = download_page(url)
    with open(file_name, "w", encoding=ENCODING) as file:
        file.write(page.text)

def load_page_from_file(file_name=PAGE_FILE):
    class Dumy:
        text = ""
    page = Dumy()
    with open(file_name, "r", encoding=ENCODING) as file_name:
        page.text = file_name.read()
    return page