import bs4
from link_to_file import *
from basic_colors import *
from download_page_search import *

import logging

# Nastavení loggeru na začátek souboru (před class Datoid_downloader)
logging.basicConfig(
    filename="datoid_downloader.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s: %(message)s",
    encoding="utf-8"
)

class Datoid_downloader(Download_page_search):
    """
    Downloader from: datoid.cz
    """
    webpage = "https://datoid.cz"
    
    def __init__(self):
        pass

    def search(self, prompt, file_type="all", search_type="relevance") -> 'Generator[Link_to_file, None, None]':
        """
        Search for files on Datoid.cz.
        Returns a generator of Link_to_file objects.
        """
        if prompt is None:
            return None
        url = Datoid_downloader.generate_search_url(prompt, file_type, search_type)
        page = download_page(url)
        return Datoid_downloader.parse_catalogue(page)
    
    @staticmethod
    def generate_search_url(prompt, file_type="all", search_type="relevance"):
        """
        Generate search URL from input atributes.

        TODO: -{Datoid_downloader.search_types[search_type]}
        """
        return f"{Datoid_downloader.webpage}/s/{prompt.replace(' ', '-')}?key=categories&value={Datoid_downloader.file_types[file_type]}"
    
    @staticmethod
    def get_atributes_from_catalogue(soup) -> Link_to_file:
        try:
            a_tag = soup.find("a")
            link = Datoid_downloader.webpage + a_tag.get("href")
            title = a_tag.find("span", class_="filename").text.strip()
            size_span = a_tag.find("i", class_="icon-size-white").parent
            size = size_span.text.strip()
            link_2_file = Link_to_file(title, link, size)
        except Exception as e:
            raise ValueError("unable to parse atributes." + str(e))
        return link_2_file
    
    @staticmethod
    def get_atributes_from_file_page(soup) -> Link_to_file:
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
            link_2_file = Link_to_file(title, link, size)
        except Exception as e:
            raise ValueError("unable to parse atributes." + str(e))
        return link_2_file

    @staticmethod
    def test_downloaded_file(link_2_file, download_folder) -> bool:
        """
        Test if downloaded file is valid.
        """
        raise NotImplementedError()
    
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
    def get_download_link_from_download_page(link_2_file):
        """
        Získá skutečný odkaz ke stažení z download page.

        {"download_link":"...","download_link_cdn":"...","wait":30}
        """
        request = "?request=1"
        response = requests.get(link_2_file.link + request)
        if response.status_code == 200:
            json_response = response.json()
            if "download_link" in json_response and json_response["download_link"]:
                link_for_download = json_response["download_link"]
            else:
                logging.error(f"JSON response: {json_response} for file: {link_2_file.title}")
                raise ValueError("No download link found in json_post.")

            link_2_file.link = link_for_download
        else:
            raise ValueError(f"Request failed with status code {response.status_code}")

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
                download_page_content = Datoid_downloader.parse_file_page(download_page(catalogue_file.link))
                link_2_file = Datoid_downloader.get_atributes_from_file_page(download_page_content)

                Datoid_downloader.get_download_link_from_download_page(link_2_file)

                yield link_2_file
            except ValueError as e:
                print_error(str(e) + " for file: " + (catalogue_file.title if catalogue_file else "Unknown"), False)