"""
Aplikace pro stahování souborů z internetu.
Zdroje:
- https://sdilej.cz
"""

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
    # search for files
    link_2_files = Sdilej_downloader().search(prompt, file_type)
    
    print("Number of files:", len(link_2_files))
    # save files to json
    with open(JSON_FILE, "w", encoding=ENCODING) as file:
        for link_2_file in link_2_files:
            file.write(link_2_file.to_json() + "\n")
    
    
    # load files from json
    link_2_files = []
    link_2_file = Link_to_file("", "", "")
    with open(JSON_FILE, "r") as file:
        for line in file:
            link_2_file = link_2_file.from_json(line)
            print(link_2_file)
            link_2_files.append(link_2_file)
            
    
    """
    page = load_page_from_file()
    link_2_files = parse_catalogue(page)
    print("Number of files:", len(link_2_files))
    # save files to json
    with open(JSON_FILE, "w", encoding=ENCODING) as file:
        file.write("[\n")
        for link_2_file in link_2_files:
            file.write(link_2_file.to_json() + ",\n")
        file.write("]\n")
    link_2_file = link_2_files[0]
    
    link_2_file_array = []
    with open(JSON_FILE, "r") as file:
        link_2_file_array = json.load(file)
    for item in link_2_file_array:
        link_2_file = Link_to_file(item.title, item.link, item.size)
        print(link_2_file)
        
    """
    
    # donwload file
    #print(link_2_file)
    #link_2_file.download(download_folder)
    
