import bs4
import logging
import requests
from src.link_to_file import Link_to_file
from basic_colors import *
from src.downloader.page_search import *

class Datoid_downloader(Download_page_search):
    """
    Downloader from: datoid.cz
    """
    webpage = "https://datoid.cz"

    logger = logging.getLogger("Datoid_downloader")
    if not logger.hasHandlers():
        handler = logging.FileHandler("datoid_downloader.log", encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    def __init__(self):
        pass

    def search(self, prompt, file_type="all", search_type="relevance") -> 'Generator[Link_to_file, None, None]':
        """
        Search for files on Datoid.cz.
        Returns a generator of Link_to_file objects.
        """
        if prompt is None or prompt.strip() == "":
            raise ValueError("Prompt cannot be empty.")
        url = Datoid_downloader.generate_search_url(prompt, file_type, search_type)
        Datoid_downloader.logger.info(f"Searching Datoid with URL: {url}")
        response = download_page(url)
        Datoid_downloader.logger.info(f"Response received: {response.status_code}")
        return Datoid_downloader.parse_catalogue(response)
    # TODO: implement next page
    
    @staticmethod
    def generate_search_url(prompt, file_type="all", search_type="relevance"):
        """
        Generate search URL from input atributes.

        TODO: -{Datoid_downloader.search_types[search_type]}
        """
        return f"{Datoid_downloader.webpage}/s/{prompt.replace(' ', '-')}?key=categories&value={Datoid_downloader.file_types[file_type]}"
    
    @staticmethod
    def get_atributes_from_catalogue(soup) -> "Link_to_file":
        try:
            a_tag = soup.find("a")
            link = Datoid_downloader.webpage + a_tag.get("href")
            title = a_tag.find("span", class_="filename").text.strip()
            size_span = a_tag.find("i", class_="icon-size-white").parent
            size = size_span.text.strip()
            link_2_file = Link_to_file(title, link, size, Datoid_downloader)
        except Exception as e:
            raise ValueError("unable to parse atributes." + str(e))
        return link_2_file
    
    @staticmethod
    def get_atributes_from_file_page(soup) -> "Link_to_file":
        try:
            # Název souboru z <h1>
            title = soup.find("h1").text.strip()
            size = None
            # Získání údajů z tabulky parametrů
            table = soup.find("table", class_="parameters")
            if table:
                params = {}
                for row in table.find_all("tr"):
                    th = row.find("th")
                    td = row.find("td")
                    if th and td:
                        key = th.text.strip().replace(":", "")
                        value = td.text.strip()
                        params[key] = value
                # Název souboru
                if "Název souboru" in params:
                    title = params["Název souboru"]
                # Velikost
                if "Velikost" in params:
                    size = params["Velikost"]
                # Typ souboru a Titul lze také použít dle potřeby (params.get("Typ souboru"), params.get("Titul"))
            # Odkaz ke stažení
            a_tag = soup.find("a", class_="btn-download")
            link = Datoid_downloader.webpage + a_tag.get("href")
            link_2_file = Link_to_file(title, link, size, Datoid_downloader)
        except Exception as e:
            raise ValueError("unable to parse atributes." + str(e))
        return link_2_file

    @staticmethod
    def test_downloaded_file(link_2_file, download_folder) -> bool:
        return Download_page_search.test_downloaded_file(link_2_file, download_folder)
    
    @staticmethod
    def parse_file_page(page):
        """
        Parse the file page and return the content.
        
        if not Datoid_downloader.is_valid_download_page(page):
            raise ValueError("Status code: " + str(page.status_code) + ". Invalid download page: no file to download.")
        """
        soup = bs4.BeautifulSoup(page.text, "html.parser")
        content = soup.find("div", id="main")
        return content
    
    @staticmethod
    def get_download_link_from_detail(detail_url: str) -> str:
        """
        Získá přímý odkaz ke stažení ze stránky s detailem souboru na datoid.cz.
        """
        request = "?request=1"
        response = requests.get(detail_url + request)
        if response.status_code != 200:
            Datoid_downloader.logger.error(f"Request failed with status code {response.status_code} for detail URL: {detail_url}")
            raise ValueError(f"Request failed with status code {response.status_code}")
        
        try:
            json_response = response.json()
        except Exception as e:
            Datoid_downloader.logger.error(f"Failed to decode JSON response for detail URL: {detail_url}. Error: {e}")
            raise ValueError("Failed to decode JSON response.") from e
        
        if "download_link" in json_response and json_response["download_link"]:
            return json_response["download_link"]
        else:
            Datoid_downloader.logger.error(f"JSON response: {json_response} for detail URL: {detail_url}")
            raise ValueError("No download link found in json_response.")

    @staticmethod
    def parse_catalogue(page) -> 'Generator[Link_to_file, None, None]':
        """
        Postupně prochází stránku s výsledky vyhledávání a vrací informace o souborech.

        yield: Link_to_file
        """
        soup = bs4.BeautifulSoup(page.text, "html.parser")
        content = soup.find("ul", class_="list", id="snippet--search_files")
        if content is None:
            return None
        content = remove_style(content)
        for videobox in content.find_all("li"):
            catalogue_file = None
            try:
                catalogue_file = Datoid_downloader.get_atributes_from_catalogue(videobox)
                download_page_content = Datoid_downloader.parse_file_page(download_page(catalogue_file.detail_url))
                link_2_file = Datoid_downloader.get_atributes_from_file_page(download_page_content)
                yield link_2_file
            except ValueError as e:
                print_error(str(e) + " for file: " + (catalogue_file.title if catalogue_file else "Unknown"), False)