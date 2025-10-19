from __future__ import annotations
import logging
import bs4
from src.download import *
from basic_colors import *
from src.downloader.page_search import *
from src.link_to_file import Link_to_file, compare_sizes

class Sdilej_downloader(Download_page_search):
    """
    Downloader from: sdilej.cz
    """
    webpage = "https://sdilej.cz"

    logger = logging.getLogger("Sdilej_downloader")
    if not logger.hasHandlers():
        handler = logging.FileHandler("sdilej_downloader.log", encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    def __init__(self):
        pass
    
    def search(self, prompt, file_type="all", search_type="relevance") -> 'Generator[Link_to_file, None, None]':
        if prompt is None or prompt.strip() == "":
            raise ValueError("Prompt cannot be empty.")
        url = Sdilej_downloader.generate_search_url(prompt, file_type, search_type)
        Sdilej_downloader.logger.info(f"Searching Sdilej with URL: {url}")
        response = requests.get(url)
        Sdilej_downloader.logger.info(f"Response received: {response.status_code}")
        return Sdilej_downloader.parse_catalogue(response)

    @staticmethod
    def generate_search_url(prompt, file_type="all", search_type="relevance"):
        """
        generate url from input
        """
        return f"{Sdilej_downloader.webpage}/{prompt}/s/{Sdilej_downloader.file_types[file_type]}-{Sdilej_downloader.search_types[search_type]}"

    @staticmethod
    def get_atributes_from_catalogue(soup) -> Link_to_file:
        try:
            link = soup.find("a").get("href")
            title = soup.find("a").get("title")
            size = soup.find_all("p")[1].text
            link_2_file = Link_to_file(title, link, size, Sdilej_downloader)
        except Exception as e:
            raise ValueError("ERROR: unable to parse atributes." + str(e))
        return link_2_file

    @staticmethod
    def get_atributes_from_file_page(soup) -> Link_to_file:
        try:
            title = soup.find("h1").text
            size = soup.find("b").next_sibling.replace("|", "").strip()
            link = Sdilej_downloader.webpage+str(soup.find("a", class_="btn btn-danger").get("href"))
            link_2_file = Link_to_file(title, link, size, Sdilej_downloader)
        except Exception as e:
            raise ValueError("Download button not found on detail page." + str(e))
        return link_2_file
    
    @staticmethod
    def get_download_link_from_detail(detail_url: str) -> str:
        """
        Získá přímý odkaz ke stažení ze stránky s detailem souboru na sdilej.cz.
        """
        page = download_page(detail_url)
        soup = bs4.BeautifulSoup(page.text, "html.parser")
        # Najdi tlačítko pro stažení
        download_btn = soup.find("a", class_="btn btn-danger")
        if not download_btn:
            raise ValueError("Download button not found on detail page for: {}".format(detail_url))
        download_link = Sdilej_downloader.webpage + str(download_btn.get("href"))
        return download_link

    @staticmethod
    def is_valid_download_page(page) -> bool:
        """
        Stránka neplatná, pokud obsahuje: 
        <h1 class="red">Stahuj a nahrávej soubory neomezenou rychlostí</h1>
        "Tento soubor byl smazán."
        """
        soup = bs4.BeautifulSoup(page.text, "html.parser")
        invalid_texts = (
            "Stahuj a nahrávej soubory neomezenou rychlostí", 
            "Chyba 404 Nenalezeno",
            "Tento soubor byl smazán."
        )
        page_title = soup.find("h1", class_="red")
        if page_title is not None and page_title.text in invalid_texts:
            return False
        
        soup = remove_style(soup)
        page_txt = soup.find("div", class_="content")
        if page_txt is not None:
            text = remove_empty_lines(page_txt.text)
            if any_text_coresponds_to(text, invalid_texts):
                return False
        return True
    
    @staticmethod
    def test_downloaded_file(link_2_file, download_folder) -> bool:
        file_size = os.path.getsize(f"{download_folder}/{link_2_file.title}")
        if file_size == 0:
            raise ValueError("ERROR: File is empty.")
        elif link_2_file.size != None and file_size < 1024:
            file = os.path.join(download_folder, link_2_file.title)
            data = open(file, "r", encoding='utf-8').read()
            return Sdilej_downloader.test_downloaded_data(data)
        elif link_2_file.size != None and not compare_sizes(file_size, link_2_file.size, 20/100):
            raise ValueError("ERROR: File size does not match.")
        return True

    @staticmethod
    def test_downloaded_data(data) -> bool:
        """
        Tests the downloaded data.
        The data is invalid if a sufficient timeout has occurred.
        If the page contains:
        "<script>top.location.href='https://sdilej.cz/free-stahovani';</script>"
        "<h1 class=\"red\">Stahování více souborů najednou</h1>"
        """
        if data is None:
            raise ValueError("ERROR: No data downloaded.")
        if "<script>top.location.href='https://sdilej.cz/free-stahovani';</script>" in data:
            raise InsufficientTimeoutError()
        if "<h1 class=\"red\">Stahování více souborů najednou</h1>" in data:
            raise InsufficientTimeoutError()
        return True

    @staticmethod
    def parse_file_page(page):
        if not Sdilej_downloader.is_valid_download_page(page):
            raise ValueError("Status code: " + str(page.status_code) + ". Invalid download page: no file to download.")
        soup = bs4.BeautifulSoup(page.text, "html.parser")
        content = soup.find("div", class_="content")
        content = soup.find("div", class_="col-md-12 col-sm-12 detail-leftcol")
        return content

    @staticmethod
    def parse_catalogue(page) -> 'Generator[Link_to_file, None, None]':
        """
        Iterates through the search results page and returns information about the files.

        Yields: Link_to_file
        """
        soup = bs4.BeautifulSoup(page.text, "html.parser")
        content = soup.find("div", class_="row post")
        if content is None:
            return None
        content = remove_style(content)
        for videobox in content.find_all(class_="videobox-desc"):
            catalogue_file = None
            try:
                catalogue_file = Sdilej_downloader.get_atributes_from_catalogue(videobox)
                download_page_content = Sdilej_downloader.parse_file_page(download_page(catalogue_file.detail_url))
                link_2_file = Sdilej_downloader.get_atributes_from_file_page(download_page_content)
                link_2_file.detail_url = catalogue_file.detail_url  # zachovej původní detail_url!
                yield link_2_file
            except ValueError as e:
                print_error(str(e) + " for file: " + (catalogue_file.title if catalogue_file else "Unknown"), False)
