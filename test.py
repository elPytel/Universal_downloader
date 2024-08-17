import pytermgui as ptg


# Funkce pro přidání URL
def search():
    """
    search:
    prompt: search, drop_down: file_type, drop_down: search_type
    """
    with ptg.WindowManager() as manager:
        menu = ptg.Window(
            ptg.InputField("", prompt="Enter URL: "),)
        manager.add(ptg.Window("Search", menu))
        manager.run()
        # Zde přidejte logiku pro přidání URL do seznamu stahování


# Funkce pro zobrazení seznamu stahování
def show_downloads():
    with ptg.WindowManager() as manager:
        downloads = ptg.Label(
            "No downloads yet"
        )  # Zde nahraďte skutečným seznamem stahování
        manager.add(ptg.Window("Downloads", downloads))
        manager.run()


# Funkce pro spuštění stahování
def start_downloads():
    # Zde přidejte logiku pro spuštění stahování
    print("Starting downloads...")


# Hlavní funkce
def main():
    with ptg.WindowManager() as manager:
        main_window = ptg.Window(
            "Main Menu",
            ptg.Splitter(
                ptg.Button("Search", lambda *_: search()),
                ptg.Button("Show Downloads", lambda *_: show_downloads()),
                ptg.Button("Start Downloads", lambda *_: start_downloads()),
                ptg.Button("Exit", lambda *_: manager.stop()),
                orientation="horizontal",
            ),
            box="DOUBLE",
            width=90,
            is_static=True,
        )
        manager.add(main_window)
        manager.run()


if __name__ == "__main__":
    main()
