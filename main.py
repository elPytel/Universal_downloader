"""
Aplikace pro stahování souborů z internetu.
Zdroje:
- https://sdilej.cz
"""

from tui import *
from pytermgui.pretty import pprint
from link_to_file import *
from sdilej_downloader import Sdilej_downloader
import argparse 

JSON_FILE = "files.json"
DEBUG = True
VERBOSE = True

download_folder = "download"

prompt = "zemeplocha"
file_type = "archive"

prompt = "karel capek"
file_type = "audio"


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(description="Download files from internet.")
    parser.add_argument("-s", "--search", type=str, help="Search for files.")
    parser.add_argument("-t", "--file-type", type=str, choices=Sdilej_downloader().file_types.keys(), help="Type of files to search for.")
    parser.add_argument("-T", "--search-type", type=str, choices=Sdilej_downloader().search_types.keys(),help="Search format.")
    parser.add_argument("-d", "--download", action="store_true", help="Download the found files.")
    parser.add_argument("-f", "--file", type=str, help="File to download.")
    parser.add_argument("-F", "--folder", type=str, help="Folder to download to.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode.")
    parser.add_argument("-D", "--debug", action="store_true", help="Debug mode.")
    parser.add_argument("-g", "--tui", action="store_true", help="Start TUI.")
    args = parser.parse_args()
    
    if args.verbose:
        VERBOSE = True
    
    if args.debug:
        DEBUG = True
    
    if args.folder:
        # folder exists?
        if not os.path.exists(args.folder):
            raise ValueError(f"Directory {args.folder} does not exist!")
        download_folder = args.folder
    
    if args.file:
        JSON_FILE = args.file
    
    if args.tui:
        main()
        exit(0)
    
    # search for files
    if args.search:
        prompt = args.search
        file_type = args.file_type if args.file_type else "all"
        search_type = args.search_type if args.search_type else "relevance"
                
        link_2_files = Sdilej_downloader().search(prompt, file_type, search_type)
        
        print_info("Number of files:", len(link_2_files))
        save_links_to_file(link_2_files, JSON_FILE, append=False)
        
    if args.download:
        link_2_files = load_links_from_file(JSON_FILE)
        for link in link_2_files:
            # test if file exists
            if os.path.exists(f"{download_folder}/{link.title}"):
                print_info(f"File {link.title} already exists.")
                continue
            
            # download file
            link.download(download_folder)
            print_success(f"Downloaded: {link.title}")
