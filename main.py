"""
Aplikace pro stahování souborů z internetu.
Zdroje:
- https://sdilej.cz
"""

from tui import *
from pytermgui.pretty import pprint
from link_to_file import *
from sdilej_downloader import Sdilej_downloader

JSON_FILE = "files.json"
DEBUG = True
VERBOSE = True

download_folder = "download"

prompt = "zemeplocha"
file_type = "archive"

prompt = "karel capek"
file_type = "audio"


if __name__ == "__main__":
    
    main()
    
    # search for files
    """
    link_2_files = Sdilej_downloader().search(prompt, file_type)
    
    print("Number of files:", len(link_2_files))
      
    # donwload file
    #print(link_2_file)
    #link_2_file.download(download_folder)
    """
