"""
Aplikace pro stahování souborů z internetu.
Zdroje:
- https://sdilej.cz
"""

import pytermgui as ptg
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

OUTPUT = {}

CONFIG = """
config:
    InputField:
        styles:
            prompt: dim italic
            cursor: '@72'
    Label:
        styles:
            value: dim bold

    Window:
        styles:
            border: '60'
            corner: '60'

    Container:
        styles:
            border: '96'
            corner: '96'
"""

def submit(manager: ptg.WindowManager, window: ptg.Window) -> None:
    for widget in window:
        if isinstance(widget, ptg.InputField):
            OUTPUT[widget.prompt] = widget.value
            continue

        if isinstance(widget, ptg.Container):
            label, field = iter(widget)
            OUTPUT[label.value] = field.value

    manager.stop()

if __name__ == "__main__":
    
    with ptg.YamlLoader() as loader:
        loader.load(CONFIG)

    with ptg.WindowManager() as manager:
        window = (
            ptg.Window(
                "",
                ptg.InputField("Balazs", prompt="Name: "),
                ptg.InputField("Some street", prompt="Address: "),
                ptg.InputField("+11 0 123 456", prompt="Phone number: "),
                "",
                ptg.Container(
                    "Additional notes:",
                    ptg.InputField(
                        "A whole bunch of\nMeaningful notes\nand stuff", multiline=True
                    ),
                    box="EMPTY_VERTICAL",
                ),
                "",
                ["Submit", lambda *_: submit(manager, window)],
                width=80,
                box="DOUBLE",
            )
            .set_title("[210 bold]New contact")
            .center()
        )

        # For the screenshot's sake
        window.select(0)

        manager.add(window)
    
    
    # search for files
    """
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
            if line == "":
                continue
            link_2_file = link_2_file.from_json(line)
            print(link_2_file.colorize())
            link_2_files.append(link_2_file)
    """
            
    """
    UI
    
    search:
    prompt: search, drop_down: file_type, drop_down: search_type
    
    files:
    list of files: select, name, size, source
    """
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
    
