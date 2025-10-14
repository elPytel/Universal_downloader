import bs4
import requests
from link_to_file import Link_to_file
from basic_colors import *
from download_page_search import *

import logging

logging.basicConfig(
    filename="prehrajto_downloader.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s: %(message)s",
    encoding="utf-8"
)

class Prehrajto_downloader(Download_page_search):
    """
    Downloader from: prehraj.to
    """
    webpage = "https://prehraj.to"
    
    def __init__(self):
        pass