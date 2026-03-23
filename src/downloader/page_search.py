from __future__ import annotations
import os
import re
import bs4
from src.download import *
from typing import Any, Generator

def remove_style(soup: bs4.BeautifulSoup | bs4.Tag) -> bs4.BeautifulSoup | bs4.Tag:
    """
    Removes everything between <style>...</style> tags from the content.
    """
    for style in soup("style"):
        style.decompose()
    return soup

def remove_empty_lines(text: Any) -> str:
    """
    Removes empty lines from text.
    """
    if isinstance(text, str):
        return "\n".join([line for line in text.split("\n") if line.strip() != ""])
    return ""

def normalize_to_beautifulsoup(soup: bs4.BeautifulSoup | bs4.Tag | requests.Response | str | bytes) -> bs4.BeautifulSoup:
    """
    Normalize input to a BeautifulSoup object.
    """
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
    return soup

def find_label_span_by_regex(soup, regex) -> bs4.Tag | None:
    """
    Finds a <span> whose text matches the given regex.
    """
    return soup.find("span", string=re.compile(regex, re.I))

def extract_value_from_label(label_span):
    """
    Extracts the value associated with a label span.
    It first looks for the next sibling <span>, and if not found, it checks the same <li> for a second <span>.
    """
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

def any_text_coresponds_to(text, texts) -> bool:
    """
    Check if any text corresponds to the given texts.
    """
    return any([t in text for t in texts])

class InsufficientTimeoutError(Exception):
    """
    Exception raised for insufficient timeout.
    """
    def __init__(self, message="Timeout is too short."):
        self.message = message
        super().__init__(self.message)

class Download_page_search:
    """
    Abstract class for searching download pages.
    """
    
    file_types = {
        "all": "",
        "video": "video",
        "audio": "audio",
        "archive": "archive",
        "images": "image"
    }
    search_types = {
        "relevance": "",
        "most_downloaded": "3",
        "newest": "4",
        "biggest": "1",
        "smallest": "2"
    }
        
    def __init__(self):
        raise NotImplementedError()
    
    def search(self, prompt, file_type="all", search_type="relevance") -> Generator["Link_to_file", None, None]:
        """
        Search for files on the website.
        """
        if prompt is None or prompt.strip() == "":
            raise ValueError("Prompt cannot be empty.")
        raise NotImplementedError()
    
    @staticmethod
    def generate_search_url(prompt, file_type="all", search_type="relevance") -> str:
        """
        Generate search URL from input attributes.
        """
        raise NotImplementedError()
    
    @staticmethod
    def test_downloaded_file(link_2_file, download_folder) -> bool:
        from src.link_to_file import compare_sizes
        
        file_size = os.path.getsize(f"{download_folder}/{link_2_file.title}")
        if file_size == 0:
            raise ValueError("ERROR: File is empty.")
        elif link_2_file.size != None and not compare_sizes(file_size, link_2_file.size, 20/100):
            raise ValueError("ERROR: File size does not match.")
        return True
    
    @staticmethod
    def parse_catalogue(page) -> Generator["Link_to_file", None, None]:
        """
        Parse the catalogue page and yield Link_to_file objects.
        """
        raise NotImplementedError()
    
    @staticmethod
    def get_download_link_from_detail(detail_url: str) -> str:
        """
        Get the direct download link from the detail page URL.
        """
        raise NotImplementedError()
        