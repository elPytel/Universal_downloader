
import os
import json
from download import *

DEBUG = True
VERBOSE = True

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
    
    def to_json(self):
        return json.dumps(self.__dict__)
    
    def from_json(self, json_str):
        link_2_file = Link_to_file("", "", "")
        link_2_file.__dict__ = json.loads(json_str)
        return link_2_file

    def __str__(self):
        return f"Title: {self.title} \nLink: {self.link} \nSize: {self.size}\n"
