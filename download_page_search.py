from typing import Any, Generator
from link_to_file import Link_to_file
import bs4

def remove_style(soup: bs4.BeautifulSoup) -> bs4.BeautifulSoup:
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
    
    def search(self, prompt, file_type="all", search_type="relevance") -> Generator[Link_to_file, None, None]:
        """
        Search for files on the website.
        """
        raise NotImplementedError()
    
    @staticmethod
    def generate_search_url(prompt, file_type="all", search_type="relevance") -> str:
        """
        Generate search URL from input attributes.
        """
        raise NotImplementedError()
    
    @staticmethod
    def test_downloaded_file(link_2_file, download_folder) -> bool:
        """
        Test if downloaded file is valid.
        """
        raise NotImplementedError()
    
    @staticmethod
    def parse_catalogue(page) -> 'Generator[Link_to_file, None, None]':
        """
        Parse the catalogue page and yield Link_to_file objects.
        """
        raise NotImplementedError()