import pytermgui as ptg
import sdilej_downloader
from link_to_file import *

LINKS = []

def drop_down(
    manager: ptg.WindowManager, button: ptg.Button, title: str, options: list
):
    """
    render a drop down menu
    """

    def select_option(option):
        button.label = option
        window.close()

    window = (
        ptg.Window(
            ptg.Container(
                *[
                    ptg.Button(option, lambda _, opt=option: select_option(opt))
                    for option in options
                ],
                orientation="vertical",
                box="EMPTY",
            ),
            width=max(len(title) + 4, max(len(option) for option in options) + 4),
            height=len(options) - 3,
        )
        .set_title(title)
        .center()
    )
    manager.add(window)


# Funkce pro přidání URL
def search(manager: ptg.WindowManager):
    """
    search:
    prompt: search, drop_down: file_type, drop_down: search_type
    """
    downloader = sdilej_downloader.Sdilej_downloader
    file_types = downloader.file_types.keys()
    search_types = downloader.search_types.keys()
    file_type = "all"
    search_type = "relevance"

    file_type_button = ptg.Button(
        file_type,
        lambda *_: drop_down(manager, file_type_button, "Select file type", file_types),
    )

    search_type_button = ptg.Button(
        search_type,
        lambda *_: drop_down(
            manager, search_type_button, "Select search type", search_types
        ),
    )

    search_field = ptg.InputField("", prompt="Enter search query: ")

    def search_files_and_close(search_text, file_type, search_type):
        console_print("Searching...")
        window.close()
        # LINKS = sdilej_downloader.Sdilej_downloader().search(search_text, file_type, search_type)
        LINKS = load_links_from_file()
        update_selected_links(selected)

    search_button = ptg.KeyboardButton(
        "Search",
        lambda *_: search_files_and_close(
            search_field.value, file_type_button.label, search_type_button.label
        ),
    )

    window = (
        ptg.Window(
            search_field,
            search_button,
            ptg.Splitter(
                "File type: ",
                file_type_button,
            ),
            ptg.Splitter(
                "Search type: ",
                search_type_button,
            ),
            width=50,
        )
        .set_title("Search")
        .center()
    )
    manager.add(window)


# Funkce pro zobrazení seznamu stahování
def show_selected(manager):
    downloads = ptg.Label(
        "No downloads yet"
    )  # Zde nahraďte skutečným seznamem stahování
    window = (
        ptg.Window(
            downloads,
            ptg.Button("Close", lambda *_: window.close()),
        )
        .set_title("Downloads")
        .center()
    )
    manager.add(window)


# Funkce pro spuštění stahování
def start_downloads(manager, text):
    # Zde přidejte logiku pro spuštění stahování
    console_print("Starting downloads...")


console_height = 5
console_text = ptg.Label("", parent_align=0)


def console_print(text):
    lines = console_text.value.split("\n")
    if len(lines) > console_height - 2:
        lines.pop(0)
    console_text.value = "\n".join(lines) + "\n" + text


def link_to_file_to_checkbox_new(link_to_file):
    """
    files:
    list of files: select, name, size, source
    """
    line_with_checkbox = ptg.Splitter(
        ptg.Container(ptg.Checkbox(), static_width=3, box="EMPTY"),
        ptg.Container(ptg.Label(link_to_file.title, parent_align=0), box="EMPTY"),
        ptg.Container(
            link_to_file.size, static_width=len(link_to_file.size), box="EMPTY"
        ),
        ptg.Container(
            link_to_file.server_name(),
            static_width=len(link_to_file.server_name()),
            box="EMPTY",
        ),
        ptg.Container(
            link_to_file.link, static_width=len(link_to_file.link), box="EMPTY"
        ),
        parent_align=0,
    )
    return line_with_checkbox


def link_to_file_to_checkbox(link_to_file):
    """
    files:
    list of files: select, name, size, source
    """
    line_with_checkbox = ptg.Splitter(
        ptg.Container(ptg.Checkbox(), static_width=3, box="EMPTY"),
        ptg.Container(ptg.Label(link_to_file.title, parent_align=0), box="EMPTY"),
        ptg.Container(
            link_to_file.size, static_width=len(link_to_file.size), box="EMPTY"
        ),
        ptg.Container(
            link_to_file.server_name(),
            static_width=len(link_to_file.server_name()),
            box="EMPTY",
        ),
        ptg.Container(
            link_to_file.link, static_width=len(link_to_file.link), box="EMPTY"
        ),
        parent_align=0,
    )
    return line_with_checkbox


selected = None


def update_selected_links(window):
    # Aktualizujte obsah okna
    # window.clear()
    for link in LINKS:
        window.add(link_to_file_to_checkbox(link))
    console_print("Selected files (Updated)")


# Hlavní funkce
def main():
    
    LINKS = load_links_from_file()

    with ptg.WindowManager() as manager:
        main_menu = ptg.Window(
            ptg.Splitter(
                ptg.KeyboardButton("Search", lambda *_: search(manager)),
                ptg.Button("Show Selected", lambda *_: show_selected(manager)),
                ptg.KeyboardButton(
                    "Download selected", lambda *_: start_downloads(manager, console_text)
                ),
                ptg.KeyboardButton("Quit", lambda *_: manager.stop()),
            ),
            box="SINGLE",
            static_height=3,
        ).set_title("Main Menu")

        selected_height = ptg.Terminal().height - main_menu.height - console_height - 15
        selected = ptg.Window(
            *[link_to_file_to_checkbox(link) for link in LINKS],
            box="SINGLE",
            static_height=selected_height,
            is_static=True,
        ).set_title("Selected files")

        console = ptg.Window(
            console_text,
            height=console_height,
            box="SINGLE",
            is_static=True,
            align="LEFT",
        ).set_title("Console")

        main_window = ptg.Window(
            main_menu,
            selected,
            console,
            box="SINGLE",
            width=ptg.Terminal().width,
            is_static=True,
        ).set_title("Universal downloader")

        """
        window = ptg.Window(
            link_to_file_to_checkbox(LINKS[0]),
            width=120,
        ).center()
        """

        manager.add(main_window)
        # manager.add(window)
        manager.run()


CONFIG = "tui.yaml"


def load_config(config_file_path=CONFIG):
    with open(config_file_path, "r") as config_file:
        config = config_file.read()
        if config == "":
            return False
        with ptg.YamlLoader() as loader:
            loader.load(config)
    return True


if __name__ == "__main__":
    # load_config()

    main()
