import os
import json
from typing import List
from download import *
from basic_colors import *

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

def compare_sizes(size1 : str, size2 : str, precision=0.1) -> bool:
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
    def __init__(self, title, link, size):
        self.title = title
        self.link = link
        self.size = size

    def download(self, download_folder="."):
        """
        Stáhne soubor z internetu a uloží jej do souboru.
        """
        file_path = os.path.join(download_folder, self.title)
        if not os.path.exists(download_folder):
            raise ValueError(f"Directory {download_folder} does not exist!")
        if os.path.exists(file_path):
            raise ValueError(f"File {self.title} already exists.")

        response = download_page(self.link)
        save_binary_file(response, file_path)
    
    def download_with_progress(self, download_folder="."):
        raise NotImplementedError("Not implemented yet.")

    def server_name(self):
        return self.link.split("/")[2]

    def to_json(self):
        return json.dumps(self.__dict__)

    def from_json(self, json_str):
        link_2_file = Link_to_file("", "", "")
        link_2_file.__dict__ = json.loads(json_str)
        return link_2_file

    def colorize(self):
        return f"Title: {Blue}{self.title}{NC} \nLink: {Blue}{self.link}{NC} \nSize: {Blue}{self.size}{NC}"

    def __str__(self):
        return f"Title: {self.title} \nLink: {self.link} \nSize: {self.size}"

    def __eq__(self, other):
        return (
            self.title == other.title
            and self.link == other.link
            and self.size == other.size
        )
    
    def __hash__(self):
        return hash((self.title, self.link, self.size))


def load_links_from_file(file_path=JSON_FILE) -> List[Link_to_file]:
    """
    load files from json
    """
    link_2_files = []
    link_2_file = Link_to_file("", "", "")
    with open(file_path, "r") as file:
        for line in file:
            if line == "":
                continue
            link_2_file = link_2_file.from_json(line)
            link_2_files.append(link_2_file)
    return link_2_files

def save_links_to_file(link_2_files: List[Link_to_file], file_path=JSON_FILE, append=False):
    """
    save files to json
    """
    if append:
        mode = "a"
    else:
        mode = "w"

    with open(file_path, mode, encoding=ENCODING) as file:
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