import bs4

def remove_style(soup: bs4.BeautifulSoup) -> bs4.BeautifulSoup:
    """
    Odstraní vše mezi tagy: <style>...</style> z obsahu content.
    """
    for style in soup("style"):
        style.decompose()
    return soup

def remove_empty_lines(text) -> str:
    return "\n".join([line for line in text.split("\n") if line.strip() != ""])

def any_text_coresponds_to(text, texts) -> bool:
    return any([t in text for t in texts])

class InsufficientTimeoutError(Exception):
    """Exception raised for insufficient timeout."""
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
        pass
    
    def search(self, prompt, file_type="all", search_type="relevance"):
        raise NotImplementedError()
    
    @staticmethod
    def test_downloaded_file(link_2_file, download_folder) -> bool:
        """
        Test if downloaded file is valid.
        """
        raise NotImplementedError()