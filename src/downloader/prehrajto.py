import bs4
import re
import logging
import requests
import urllib.parse
from basic_colors import *
from src.downloader.page_search import *
from src.link_to_file import Link_to_file

class Prehrajto_downloader(Download_page_search):
    """
    Downloader from: prehraj.to
    """
    webpage = "https://prehraj.to"

    logger = logging.getLogger("Prehrajto_downloader")
    if not logger.hasHandlers():
        handler = logging.FileHandler("prehrajto_downloader.log", encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    def __init__(self):
        pass

    @staticmethod
    def generate_search_url(prompt, file_type="video", search_type=None):
        """
        Vygeneruje URL pro hledání na prehraj.to.
        """
        prompt = prompt.strip().replace(" ", "%20")
        return f"https://prehraj.to/hledej/{prompt}"
    
    def search(self, prompt, file_type="all", search_type="relevance") -> 'Generator[Link_to_file, None, None]':
        """
        Search for files on Datoid.cz.
        Returns a generator of Link_to_file objects.
        """
        if prompt is None or prompt.strip() == "":
            raise ValueError("Prompt cannot be empty.")
        url = Prehrajto_downloader.generate_search_url(prompt, file_type, search_type)
        Prehrajto_downloader.logger.info(f"Searching Prehrajto with URL: {url}")
        response = requests.get(url)
        Prehrajto_downloader.logger.info(f"Response received: {response.status_code}")
        page = response.text
        if response.status_code != 200:
            raise ValueError(f"Failed to retrieve search results, status code: {response.status_code} for URL: {url}")
        return Prehrajto_downloader.parse_catalogue(page)
    # TODO: implement next page
    # https://prehraj.to/hledej/zaklínač?vp-page=2
    
    @staticmethod
    def is_valid_download_page(page) -> bool:
        """
        Returns False when the page indicates the video is still being processed,
        e.g. contains: <div class="status status--success text-center"> Video se zpracovává </div>
        Accepts either a requests.Response-like object or raw HTML/text.
        """
        # Reject non-200 responses
        if hasattr(page, "status_code") and page.status_code != 200:
            return False

        # Get HTML/text
        if hasattr(page, "text"):
            html = page.text or ""
        else:
            html = page or ""

        if isinstance(html, bytes):
            try:
                html = html.decode("utf-8", errors="ignore")
            except Exception:
                html = str(html)

        soup = bs4.BeautifulSoup(html, "html.parser")

        # remove script/style to avoid false matches
        for tag in soup(["script", "style"]):
            tag.decompose()

        # Check status-like blocks first
        status_divs = soup.find_all("div", class_=re.compile(r"\bstatus\b"))
        for d in status_divs:
            if "video se zpracov" in d.get_text(" ", strip=True).lower():
                return False

        # Fallback: check whole page text for processing indicators
        invalid_texts = (
            "Video se zpracovává", 
            "video se zpracov",
            "zpracováv"
        )
        
        soup = remove_style(soup)
        page_text = soup.get_text(" ", strip=True).lower()
        if page_text is not None:
            text = remove_empty_lines(page_text)
            if any_text_coresponds_to(text, invalid_texts):
                return False

        # Ensure there is a download anchor present, e.g.
        # <a id="frame" href="... ?do=download" class="button cta ...">Stáhnout soubor</a>
        a_frame = soup.find("a", id="frame")
        if not a_frame:
            # try fallback: button/cta anchor containing 'stáhnout' or '?do=download' in href
            a_frame = soup.find("a", class_=re.compile(r"\b(button|cta)\b"), string=re.compile(r"stáhnout", re.I))

        if not a_frame:
            return False

        href = a_frame.get("href", "") or ""
        if "?do=download" not in href and "do=download" not in href:
            # sometimes href could be absolute or contain params; if no download param, treat as invalid
            return False

        return True


    @staticmethod
    def get_atributes_from_file_page(soup) -> "Link_to_file":
        """
        Parse file page parameters and return Link_to_file(title, url, size, Prehrajto_downloader).
        Accepts either a BeautifulSoup object, a requests.Response, or raw HTML/text.
        """
        # Accept Response or raw HTML as input — normalize to BeautifulSoup
        if not isinstance(soup, bs4.BeautifulSoup):
            if hasattr(soup, "text"):
                html = soup.text or ""
            else:
                html = soup or ""
            if isinstance(html, bytes):
                try:
                    html = html.decode("utf-8", errors="ignore")
                except Exception:
                    html = str(html)
            soup = bs4.BeautifulSoup(html, "html.parser")

        def find_label_span(regex):
            return soup.find("span", string=re.compile(regex, re.I))

        def extract_value_from_label(label_span):
            if not label_span:
                return ""
            # preferred: the following sibling <span>
            val_span = label_span.find_next_sibling("span")
            if val_span and val_span.get_text(strip=True):
                return val_span.get_text(strip=True)
            # fallback: same <li> second span
            li = label_span.find_parent("li")
            if li:
                spans = li.find_all("span")
                if len(spans) >= 2 and spans[1].get_text(strip=True):
                    return spans[1].get_text(strip=True)
            return ""

        name_label = find_label_span(r'^\s*Název souboru[:\s]*$')
        size_label = find_label_span(r'^\s*Velikost[:\s]*$')
        format_label = find_label_span(r'^\s*Formát[:\s]*$')

        name = extract_value_from_label(name_label)
        size = extract_value_from_label(size_label)
        fmt = extract_value_from_label(format_label).lower().strip()

        # Normalize filename: append extension if format present and not already there
        if fmt and name and not re.search(r'\.' + re.escape(fmt) + r'\s*$', name, re.I):
            name = f"{name}.{fmt}"
        
        # Get download anchor href and strip query/fragment (detail URL should NOT contain ?do=download)
        detail_url = ""
        a_frame = soup.find("a", id="frame")
        if a_frame:
            href = a_frame.get("href") or ""
            # remove query and fragment
            parsed = urllib.parse.urlparse(href)
            clean = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))
            # If relative, prepend domain
            if not clean.startswith("http"):
                if clean.startswith("/"):
                    detail_url = f"https://prehraj.to{clean}"
                elif clean:
                    detail_url = f"https://prehraj.to/{clean}"
            else:
                detail_url = clean

        return Link_to_file(name, detail_url, size, Prehrajto_downloader)

    @staticmethod
    def get_atributes_from_catalogue(soup) -> Link_to_file:
        """
        Získá informace o videu z katalogového HTML elementu (soup) a vrátí Link_to_file.
        """
        a_tag = soup.find("a", class_="video--link")
        if not a_tag:
            raise ValueError("Unable to find video link in the provided HTML element.")
        title = a_tag.get("title") or a_tag.find("h3", class_="video__title").text.strip()
        href = a_tag.get("href")
        detail_url = f"https://prehraj.to{href}" if href and not href.startswith("http") else href

        # Najdi velikost souboru
        size_div = a_tag.find("div", class_="video__tag--size")
        size = size_div.text.strip() if size_div else ""

        return Link_to_file(title, detail_url, size, Prehrajto_downloader)

    @staticmethod
    def parse_catalogue(page) -> 'Generator[Link_to_file, None, None]':
        """
        Prochází stránku s výsledky vyhledávání (nový formát s <div>) a vrací informace o souborech.
        yield: Link_to_file
        """
        soup = bs4.BeautifulSoup(page, "html.parser")
        # Najdi grid s výsledky (má více tříd)
        grids = soup.find_all("div", class_="grid-x")
        for grid in grids:
            # Hledáme grid, který má potomky <div> s <a class="video--link">
            for div in grid.find_all("div", recursive=False):
                a_tag = div.find("a", class_="video--link")
                link_2_file = None
                if a_tag:
                    try:
                        link_2_file = Prehrajto_downloader.get_atributes_from_catalogue(div)
                        #download_page_content = Prehrajto_downloader.parse_file_page(download_page(link_2_file.detail_url))
                        detail_page = download_page(link_2_file.detail_url)
                        if not Prehrajto_downloader.is_valid_download_page(detail_page):
                            raise ValueError(f"Status code: {detail_page.status_code}. Invalid download page: no file to download.")
                        link_2_file = Prehrajto_downloader.get_atributes_from_file_page(detail_page)
                        if link_2_file:
                            yield link_2_file
                    except ValueError as e:
                        print_error(f"{str(e)} for file: {(link_2_file.title if link_2_file else 'Unknown')}", False)
    
    @staticmethod
    def get_download_link_from_detail(detail_url: str) -> str:
        return f"{detail_url}?do=download"