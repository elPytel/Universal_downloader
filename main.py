"""
Aplikace pro stahování souborů z internetu.
Ze stránek jako:
- https://sdilej.cz
- https://datoid.cz
- https://prehrajto.cz
"""

import os
import sys
import queue
import argparse 
import threading
from time import sleep
from src.link_to_file import *
from src.downloader.sdilej import Sdilej_downloader
from src.downloader.datoid import Datoid_downloader
from src.downloader.prehrajto import Prehrajto_downloader
from src.downloader.page_search import Download_page_search

JSON_FILE = "files.json"
FAILED_FILES = "failed_files.json"
DEBUG = False
VERBOSE = True

download_folder = "download"

prompt = "karel capek"
file_type = "audio"

def read_input(input_queue):
    while True:
        input_queue.put(sys.stdin.read(1))

if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(description="Download files from internet.")
    parser.add_argument("-s", "--search", type=str, help="Search for files.")
    parser.add_argument("-t", "--file-type", type=str, choices=Download_page_search.file_types.keys(), help="Type of files to search for.")
    parser.add_argument("-T", "--search-type", type=str, choices=Download_page_search.search_types.keys(), help="Search format.")
    parser.add_argument("-d", "--download", action="store_true", help="Download the found files.")
    parser.add_argument("-f", "--file", type=str, help="File to download.")
    parser.add_argument("-F", "--folder", type=str, help="Folder to download to.")
    parser.add_argument("-n", "--number", type=int, help="Max number of files to search.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode.")
    parser.add_argument("-D", "--debug", action="store_true", help="Debug mode.")
    parser.add_argument("-g", "--tui", action="store_true", help="Start TUI.")
    parser.add_argument("-G", "--gui", action="store_true", help="Start GUI.")
    parser.add_argument("-r", "--remove", action="store_true", help="Remove downloaded files from the list.")
    args = parser.parse_args()
    
    if args.verbose:
        VERBOSE = True
        set_verbose(True)
    
    if args.debug:
        DEBUG = True
    
    if args.folder:
        # folder exists?
        if not os.path.exists(args.folder):
            raise ValueError(f"Directory {args.folder} does not exist!")
        download_folder = args.folder
    
    if args.file:
        JSON_FILE = args.file
    
    # start TUI
    if args.tui:
        import tui 
        tui.main()
        exit(0)

    # start GUI
    if args.gui:
        import gui
        gui.main()
        exit(0)

    input_queue = queue.Queue()
    input_thread = threading.Thread(target=read_input, args=(input_queue,))
    input_thread.daemon = True
    input_thread.start()

    # search for files
    if args.search:
        prompt = args.search
        file_type = args.file_type if args.file_type else "all"
        search_type = args.search_type if args.search_type else "relevance"
                
        link_2_files = []
        for i, link_2_file in enumerate(Prehrajto_downloader().search(prompt, file_type, search_type)):
            if args.number and i >= args.number:
                break
            if DEBUG:
                print("")
                print(link_2_file.colorize())
            link_2_files.append(link_2_file)
        
        print_info(f"Number of files: {len(link_2_files)}")
        add_links_to_file(link_2_files, JSON_FILE)
        
    if args.download:
        link_2_files = load_links_from_file(JSON_FILE)
        successfull_files = []
        for link_2_file in link_2_files:
            # Check for 'q' key press to exit
            if not input_queue.empty() and input_queue.get() == 'q':
                print_info("Exiting download loop.")
                break

            # test if file exists
            if os.path.exists(f"{download_folder}/{link_2_file.title}"):
                print_info(f"File {link_2_file.title} already exists.")
                successfull_files.append(link_2_file)
                continue
            
            # download file
            if VERBOSE:
                print_info(f"Downloading file: {Blue}{link_2_file.title}{NC} of size {Blue}{link_2_file.size}{NC}...")
            link_2_file.download(download_folder)
            
            # test file size > 1kb
            file_size = os.path.getsize(f"{download_folder}/{link_2_file.title}")
            if (not compare_sizes(file_size, link_2_file.size, 20/100) and link_2_file.size != None) or (link_2_file.size == None and file_size < 1024):
                print_warning(f"File {Blue}{link_2_file.title}{NC} was not downloaded correctly.")
                print_info(f"File size: {Blue}{file_size}{NC} expected: {Blue}{link_2_file.size}{NC}")
                if not DEBUG:
                    os.remove(f"{download_folder}/{link_2_file.title}")
                    print_info(f"File {Blue}{link_2_file.title}{NC} was removed.")
                save_links_to_file([link_2_file], FAILED_FILES, append=True)
            else:
                successfull_files.append(link_2_file)
                if VERBOSE:
                    print_success(f"File {Blue}{link_2_file.title}{NC} of size {Blue}{size_int_2_string(file_size)}{NC} was downloaded.")
            
            # wait
            sleep_time = 60
            print_info(f"Wating {sleep_time}s...")
            sleep(sleep_time)
        
        if args.remove and len(successfull_files) > 0:
            if VERBOSE:
                print_info("Removing downloaded files from the list...")
            remove_links_from_file(successfull_files, JSON_FILE)
