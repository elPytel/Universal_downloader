import os
import json
from download import *
from colors import *

DEBUG = True
VERBOSE = True
JSON_FILE = "files.json"


class Link_to_file:
    def __init__(self, title, link, size):
        self.title = title
        self.link = link
        self.size = size

    def download(self, download_folder="."):
        """
        Stáhne soubor z internetu a uloží jej do souboru.
        """
        file_path = f"{download_folder}/{self.title}"
        if not os.path.exists(download_folder):
            raise ValueError(f"Directory {download_folder} does not exist!")
        if os.path.exists(file_path):
            raise ValueError(f"File {self.title} already exists.")

        if VERBOSE:
            print(f"Downloading file: {self.title}")

        response = download_page(self.link)
        save_binary_file(response, file_path)

        if VERBOSE:
            print(f"File {self.title} was downloaded.")

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


def load_links_from_file(file_path=JSON_FILE):
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


def save_links_to_file(link_2_files, file_path=JSON_FILE, append=False):
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
