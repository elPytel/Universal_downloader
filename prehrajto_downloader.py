import bs4
import logging
import requests
from link_to_file import Link_to_file
from basic_colors import *
from download_page_search import *

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
                if a_tag:
                    try:
                        link_2_file = Prehrajto_downloader.get_atributes_from_catalogue(div)
                        if link_2_file:
                            yield link_2_file
                    except ValueError as e:
                        print_error(str(e) + " for file: " + (link_2_file.title if link_2_file else "Unknown"), False)
    
    
    @staticmethod
    def get_download_link_from_detail(detail_url: str) -> str:
        return f"{detail_url}?do=download"