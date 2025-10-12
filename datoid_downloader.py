import bs4
from link_to_file import *
from basic_colors import *
from download_page_search import *

class Datoid_downloader(Download_page_search):
    webpage = "https://datoid.cz"
    
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