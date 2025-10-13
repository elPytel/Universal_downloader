from __future__ import annotations
import os
import json
import requests
from typing import List
from download import *
from basic_colors import *

from download_page_search import Download_page_search

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

class Link_to_file:
    def __init__(self, title, detail_url, size, source_class: Download_page_search = None):
        self.title = title
        self.detail_url = detail_url
        self.size = size
        self.Source_class = source_class
    
    def get_download_link(self) -> str:
        """
        Get the direct download link from the detail page URL.
        """
        return self.Source_class.get_download_link_from_detail(self.detail_url)

    def download(self, download_folder="."):
        """
        Downloads a file from the internet and saves it to the specified folder.
        """
        file_path = os.path.join(download_folder, self.title)
        if not os.path.exists(download_folder):
            raise ValueError(f"Directory {download_folder} does not exist!")
        if os.path.exists(file_path):
            raise ValueError(f"File {self.title} already exists.")

        download_link = self.get_download_link()
        response = requests.get(download_link)
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
            "source_class": type(self.Source_class).__name__ if self.Source_class else None
        }

    @staticmethod
    def from_dict(data):
        from datoid_downloader import Datoid_downloader
        from sdilej_downloader import Sdilej_downloader

        SOURCE_CLASS_MAP = {
            "Sdilej_downloader": Sdilej_downloader,
            "Datoid_downloader": Datoid_downloader,
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
        return json.dumps(self.__dict__)

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
        )
    
    def __hash__(self):
        return hash((self.title, self.detail_url, self.size))


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