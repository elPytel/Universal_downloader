from __future__ import annotations
import os
import json
import requests
from time import sleep
import mimetypes
import logging
from urllib.parse import urlparse
from typing import List
from src.download import *
from basic_colors import *

from src.downloader.page_search import Download_page_search

DEBUG = True
VERBOSE = True
JSON_FILE = "files.json"

def size_int_2_string(size : int) -> str:
    """
    Converts an integer in bytes to a string with a size.
    """
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    if size < 1024 * 1024 * 1024:
        return f"{size / 1024 / 1024:.2f} MB"
    return f"{size / 1024 / 1024 / 1024:.2f} GB"

def size_string_2_bytes(size : str) -> int:
    """
    Converts a string with a size to an integer in bytes.
    """
    size = size.lower().strip()
    if size.endswith("kb"):
        return int(float(size[:-2]) * 1024)
    if size.endswith("mb"):
        return int(float(size[:-2]) * 1024 * 1024)
    if size.endswith("gb"):
        return int(float(size[:-2]) * 1024 * 1024 * 1024)
    if size.endswith("b"):
        return int(float(size[:-1]))
    return int(float(size))

def compare_sizes(size1 : int, size2 : int, precision=0.1) -> bool:
    """
    Compares two sizes of files.
    precision: 0.1 means that the sizes can differ by 10%.
    """
    # pokud je size string, převeď na int
    if isinstance(size1, str):
        size1 = size_string_2_bytes(size1)
    if isinstance(size2, str):
        size2 = size_string_2_bytes(size2)
    return size1 * (1 - precision) < size2 < size1 * (1 + precision)

def get_extension_from_title(title: str) -> str | None:
    """
    Returns the file extension from the title, including the dot (e.g. '.mp4'), or None if there is none.
    """
    _, ext = os.path.splitext(title)
    return ext if ext else None

def get_extension_from_url(url: str) -> str | None:
    """
    Returns the file extension from a URL, including the dot (e.g. '.mp4'), or None if there is none.
    """
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    return ext if ext else None

def get_response_extension(response):
    content_type = response.headers.get('Content-Type')
    ext = mimetypes.guess_extension(content_type) if content_type else None
    return ext

class Link_to_file:
    def __init__(self, title, detail_url, size, source_class: type[Download_page_search]):
        self.title = title
        self.detail_url = detail_url
        self.size = size
        self.source_class = source_class
    
    def get_download_link(self) -> str:
        """
        Get the direct download link from the detail page URL.
        """
        return self.source_class.get_download_link_from_detail(self.detail_url)

    def download(self, download_folder=".", timeout=120):
        """
        Downloads a file from the internet and saves it to the specified folder.
        """
        file_path = os.path.join(download_folder, self.title)
        if not os.path.exists(download_folder):
            raise ValueError(f"Directory {download_folder} does not exist!")
        if os.path.exists(file_path):
            raise ValueError(f"File {self.title} already exists.")

        logger = logging.getLogger("universal_downloader")
        logger.info("Starting download: title=%s detail_url=%s expected_size=%s", self.title, self.detail_url, self.size)
        try:
            get_links = getattr(self.source_class, "get_download_links_from_detail", None)
            link_info = (
                get_links(self.detail_url, timeout=timeout)
                if get_links
                else self.source_class.get_download_link_from_detail(self.detail_url, timeout=timeout)
            )
            if isinstance(link_info, str):
                download_links = [link_info]
                wait = 0
                session = requests
            else:
                download_links = link_info.links
                wait = link_info.wait
                session = link_info.session or requests
            if wait:
                logger.info("Waiting before download: title=%s seconds=%s", self.title, wait)
                sleep(wait)
            logger.info("Received direct download URL for title=%s", self.title)
            response = None
            last_error = None
            for download_link in download_links:
                try:
                    logger.info("Trying direct download URL: title=%s url=%s", self.title, download_link)
                    response = session.get(download_link, stream=True, timeout=timeout)
                    response.raise_for_status()
                    break
                except requests.RequestException as error:
                    last_error = error
                    if response is not None:
                        response.close()
                    logger.warning("Direct download URL failed: title=%s url=%s error=%s", self.title, download_link, error)
                    response = None
            if response is None:
                raise last_error or requests.RequestException("No download URL succeeded.")
            logger.info(
                "Download response: title=%s status=%s content_type=%s content_length=%s",
                self.title,
                response.status_code,
                response.headers.get("Content-Type"),
                response.headers.get("Content-Length"),
            )
            self.save_file_with_extension(response, download_folder)
            logger.info("Download completed: title=%s", self.title)
        except (requests.RequestException, ValueError, OSError):
            logger.exception("Download failed: title=%s detail_url=%s", self.title, self.detail_url)
            raise

    def save_file_with_extension(self, response, download_folder=".", ext=None):
        if not ext:
            ext = get_extension_from_title(self.title)
        if not ext:
            ext = get_response_extension(response)
        if not ext:
            ext = get_extension_from_url(self.detail_url)
        if not ext:
            ext = ""  # fallback
            print(f"Warning: Unable to determine file extension for {self.title}, using {ext} as fallback.")

        if not self.title.endswith(ext):
            self.title += ext

        file_path = os.path.join(download_folder, self.title)
        if os.path.exists(file_path):
            raise ValueError(f"File {self.title} already exists.")
        save_binary_file(response, file_path)
    
    def download_with_progress(self, download_folder="."):
        raise NotImplementedError("Not implemented yet.")

    def server_name(self):
        return self.detail_url.split("/")[2]
    
    def to_dict(self):
        return {
            "title": self.title,
            "detail_url": self.detail_url,
            "size": self.size,
            "source_class": self.source_class.__name__ if self.source_class else None
        }

    @staticmethod
    def from_dict(data):
        from src.downloader.datoid import Datoid_downloader
        from src.downloader.sdilej import Sdilej_downloader
        from src.downloader.prehrajto import Prehrajto_downloader

        SOURCE_CLASS_MAP = {
            "Sdilej_downloader": Sdilej_downloader,
            "Datoid_downloader": Datoid_downloader,
            "Prehrajto_downloader": Prehrajto_downloader,
            # případně další zdroje
        }
        source_class = SOURCE_CLASS_MAP.get(data.get("source_class"), None)
        if source_class is None:
            raise ValueError("source_class is required and was not found in SOURCE_CLASS_MAP")
        return Link_to_file(
            data.get("title"),
            data.get("detail_url"),
            data.get("size"),
            source_class
        )

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        return Link_to_file.from_dict(data)

    def colorize(self):
        return f"Title: {Blue}{self.title}{NC} \nLink: {Blue}{self.detail_url}{NC} \nSize: {Blue}{self.size}{NC}"

    def __str__(self):
        return f"Title: {self.title} \nLink: {self.detail_url} \nSize: {self.size}"

    def __eq__(self, other):
        return (
            self.title == other.title
            and self.detail_url == other.detail_url
            and self.size == other.size
            and self.source_class == other.source_class
        )
    
    def __hash__(self):
        return hash((self.title, self.detail_url, self.size, self.source_class))


def load_links_from_file(file_path=JSON_FILE) -> List[Link_to_file]:
    link_2_files = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            link_2_file = Link_to_file.from_json(line)
            link_2_files.append(link_2_file)
    return link_2_files

def save_links_to_file(link_2_files: List[Link_to_file], file_path=JSON_FILE, append=False):
    mode = "a" if append else "w"
    with open(file_path, mode, encoding="utf-8") as file:
        for link_2_file in link_2_files:
            file.write(link_2_file.to_json() + "\n")

def remove_links_from_file(links_to_remove_from_file: List[Link_to_file], file_path=JSON_FILE):
    """
    remove files from json
    """
    old_link_2_files = load_links_from_file(file_path)
    new_link_2_files = []
    for link_2_file in old_link_2_files:
        if link_2_file not in links_to_remove_from_file:
            new_link_2_files.append(link_2_file)
    save_links_to_file(new_link_2_files, file_path)

def add_links_to_list(old_links: List[Link_to_file], new_links: List[Link_to_file]) -> List[Link_to_file]:
    """
    add files to list
    """
    return list(set(old_links + new_links))

def add_links_to_file(links_to_add_to_file: List[Link_to_file],  file_path=JSON_FILE):
    """
    add files to json
    """
    old_link_2_files = load_links_from_file(file_path)
    save_links_to_file(add_links_to_list(old_link_2_files, links_to_add_to_file), file_path)