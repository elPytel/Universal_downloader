from __future__ import annotations
import os
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
        