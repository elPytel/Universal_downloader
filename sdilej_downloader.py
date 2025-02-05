
import bs4
from link_to_file import *
from basic_colors import *

def remove_style(soup):
    """
    Odstraní vše mezi tagy: <style>...</style> z obsahu content.
    """
    for style in soup("style"):
        style.decompose()
    return soup

class Download_page_search:
    
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
    
    def search(self, prompt, file_type="all", search_type="relevance"):
        raise NotImplementedError()

class Sdilej_downloader(Download_page_search):
    webpage = "https://sdilej.cz"
    
    def __init__(self):
        pass
    
    def search(self, prompt, file_type="all", search_type="relevance"):
        url = Sdilej_downloader.generate_search_url(prompt, file_type, search_type)
        page = download_page(url)
        link_2_files = parse_catalogue(page)
        return link_2_files
    
    def generate_search_url(prompt, file_type="all", search_type="relevance"):
        """
        generate url from input
        """
        return f"{Sdilej_downloader.webpage}/{prompt}/s/{Sdilej_downloader.file_types[file_type]}-{Sdilej_downloader.search_types[search_type]}"

def get_atributes_from_catalogue(soup):
    try:
        link = soup.find("a").get("href")
        title = soup.find("a").get("title")
        size = soup.find_all("p")[1].text
        link_2_file = Link_to_file(title, link, size)
    except Exception as e:
        raise ValueError("ERROR: unable to parse atributes." + str(e))
    return link_2_file

def get_atributes_from_file_page(soup):
    # h1, style"font-size:23px", text
    try:
        title = soup.find("h1").text
        size = soup.find("b").next_sibling.strip()
        link = Sdilej_downloader.webpage+str(soup.find("a", class_="btn btn-danger").get("href"))
        link_2_file = Link_to_file(title, link, size)
    except Exception as e:
        raise ValueError("ERROR: unable to parse atributes." + str(e))
    return link_2_file

def remove_empty_lines(text):
    return "\n".join([line for line in text.split("\n") if line.strip() != ""])

def any_text_coresponds_to(text, texts):
    return any([t in text for t in texts])

def is_valid_download_page(page):
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
    text = remove_empty_lines(page_txt.text)
    if page_txt is not None and any_text_coresponds_to(text, invalid_texts):
        return False
    return True

def parse_file_page(page):
    if not is_valid_download_page(page):
        raise ValueError("Status code: " + str(page.status_code) + ". Invalid download page: no file to download.")
    soup = bs4.BeautifulSoup(page.text, "html.parser")
    content = soup.find("div", class_="content")
    content = soup.find("div", class_="col-md-12 col-sm-12 detail-leftcol")
    return content

def parse_catalogue(page):
    """
    Vrátí obsah článku.
    """
    soup = bs4.BeautifulSoup(page.text, "html.parser")
    content = soup.find("div", class_="row post")
    content = remove_style(content)
    link_2_files = []
    for videobox in content.find_all(class_="videobox-desc"):
        try:
            catalogue_file = get_atributes_from_catalogue(videobox)
            if DEBUG:
                print("")
                print(catalogue_file.colorize())
            download_page_content = parse_file_page(download_page(catalogue_file.link))
            link_2_file = get_atributes_from_file_page(download_page_content)
            link_2_files.append(link_2_file)
        except ValueError as e:
            print_error(str(e) + " for file: " + catalogue_file.title, False)
    return link_2_files

