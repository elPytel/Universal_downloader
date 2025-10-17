import os
import sys
import json
import time
import queue
import shutil
import gettext
import argparse
import threading
import subprocess
import tkinter as tk
from tkinter import ttk
from link_to_file import *
from PIL import ImageTk
from sdilej_downloader import Sdilej_downloader
from datoid_downloader import Datoid_downloader
from prehrajto_downloader import Prehrajto_downloader
from main import download_folder, JSON_FILE
from download_page_search import Download_page_search, InsufficientTimeoutError

CONFIG_FILE = "config.json"
DEFAULT_LANGUAGE = "en"
TIME_OUT = 50

LANGUAGES = {
    'EN': 'en',
    'CZ': 'cs'
}

SOURCES = [
    {"name": "Sdilej.cz", "class": Sdilej_downloader, "timeout": TIME_OUT},
    {"name": "Datoid.cz", "class": Datoid_downloader, "timeout": TIME_OUT},
    {"name": "Prehraj.to", "class": Prehrajto_downloader, "timeout": TIME_OUT},
]

DOMAIN = 'universal_downloader'
ICON_FILE = 'icon.png'
ASSETS_DIR = 'assets'

def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    """
    if hasattr(sys, "_MEIPASS"):
        # Cesta k dočasné složce při spuštění .exe
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def compile_mo_files():
    """
    Compiles .po files to .mo files using msgfmt.
    If msgfmt is not found, skips compilation (Typically on target machine with .exe).
    """
    localedir = get_resource_path("locales")
    msgfmt_path = shutil.which('msgfmt')
    if not msgfmt_path:
        print("msgfmt not found in PATH — skipping .po -> .mo compilation. Ensure .mo files are included in the build.")
        return

    for lang in LANGUAGES.values():
        po_file = os.path.join(localedir, lang, 'LC_MESSAGES', DOMAIN + '.po')
        mo_file = os.path.join(localedir, lang, 'LC_MESSAGES', DOMAIN + '.mo')
        if os.path.exists(po_file):
            if not os.path.exists(mo_file) or os.path.getmtime(po_file) > os.path.getmtime(mo_file):
                print(f"Compiling {po_file} to {mo_file}")
                try:
                    subprocess.run([msgfmt_path, '-o', mo_file, po_file], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"msgfmt failed: {e}")

class DownloaderGUI(tk.Tk):
    lang_codes = LANGUAGES.values()

    def __init__(self):
        super().__init__()
        icon_path = get_resource_path(os.path.join(ASSETS_DIR, "icon.png"))
        if os.path.isfile(icon_path):
            icon = tk.PhotoImage(file=icon_path)
            self.iconphoto(True, icon)
        else:
            print(f"Icon: '{icon_path}' not found.")
        
        self.settings = self.load_config()
        self.current_language = tk.StringVar(value=self.settings.get("language", DEFAULT_LANGUAGE))
        self.remove_successful_var = tk.BooleanVar(value=self.settings.get("remove_successful", False))
        self.remove_successful_var.trace_add("write", self.update_remove_successful)
        self.add_files_with_failed_timeout_var = tk.BooleanVar(value=self.settings.get("add_files_with_failed_timeout", False))
        self.add_files_with_failed_timeout_var.trace_add("write", self.update_add_files_with_failed_timeout)

        self.source_vars = []
        for source in SOURCES:
            var = tk.BooleanVar(value=self.settings.get(source["name"], True))
            # Save changes to config on change
            var.trace_add("write", lambda *args, name=source["name"], var=var: self.settings.update({name: var.get()}) or self.save_config())
            self.source_vars.append(var)

        self.link_map = {} # detail_url -> Link_to_file (mapping with result treeview)

        self.setup_translation()
        self.title(_("Universal Downloader"))
        self.geometry("800x600")
        self.create_widgets()

    def load_config(self, config_file=CONFIG_FILE) -> dict:
        """
        Load configuration from a JSON file.
        If the file does not exist, returns an empty dictionary.
        """
        try:
            with open(config_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        
    def save_config(self, config_file=CONFIG_FILE):
        """
        Save configuration to a JSON file.
        """
        with open(config_file, "w") as file:
            json.dump(self.settings, file)

    def setup_translation(self, domain=DOMAIN):
        lang_code = self.current_language.get()
        global _
        localedir = get_resource_path("locales")
        try:
            lang = gettext.translation(domain, localedir=localedir, languages=[lang_code])
            lang.install()
            if DEBUG:
                print_success(f"Translation loaded for {lang_code}.")
            _ = lang.gettext
        except Exception as e:
            print_error(f"Translation not found for {lang_code}, falling back to default. Error: {e}")
            gettext.install(domain, localedir=localedir)
            _ = gettext.gettext

    def create_widgets(self):
        # Menu bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=_("Save Selected"), command=self.save_selected)
        file_menu.add_command(label=_("Load from file"), command=self.load_from_file)
        menubar.add_cascade(label=_("File"), menu=file_menu)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        lang_menu = tk.Menu(settings_menu, tearoff=0)
        for lang in self.lang_codes:
            lang_menu.add_radiobutton(label=lang, variable=self.current_language, value=lang, command=self.change_language)
        settings_menu.add_cascade(label=_("Language"), menu=lang_menu)
        settings_menu.add_separator()
        settings_menu.add_checkbutton(label=_("Remove successful from json"), variable=self.remove_successful_var)
        settings_menu.add_checkbutton(label=_("Add back files with failed timeout"), variable=self.add_files_with_failed_timeout_var)
        menubar.add_cascade(label=_("Settings"), menu=settings_menu)

        # Zdroje menu
        sources_menu = tk.Menu(menubar, tearoff=0)
        for i, source in enumerate(SOURCES):
            sources_menu.add_checkbutton(
                label=source["name"],
                variable=self.source_vars[i],
                onvalue=True,
                offvalue=False
            )
        menubar.add_cascade(label=_("Sources"), menu=sources_menu)


        # Search frame
        search_frame = ttk.Frame(self)
        search_frame.pack(pady=5, padx=5, fill=tk.X)

        self.search_label = ttk.Label(search_frame, text=_("Search:"))
        self.search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # file type: show translated labels but keep internal key
        # internal vars (hold keys used by search)
        self.file_type_var = tk.StringVar(value="all")
        self.search_type_var = tk.StringVar(value="relevance")
        # display vars (hold translated label shown in OptionMenu)
        self.file_type_display_var = tk.StringVar(value=_(self.file_type_var.get()))
        self.search_type_display_var = tk.StringVar(value=_(self.search_type_var.get()))

        # build OptionMenus using display vars; commands set both internal key and display label
        self.file_type_menu = ttk.OptionMenu(search_frame, self.file_type_display_var, self.file_type_display_var.get())
        menu = self.file_type_menu["menu"]
        menu.delete(0, "end")
        for key in Download_page_search.file_types.keys():
            label = _(key)
            menu.add_command(label=label, command=lambda k=key, l=label: (self.file_type_var.set(k), self.file_type_display_var.set(l)))
        self.file_type_menu.pack(side=tk.LEFT, padx=5)

        self.search_type_menu = ttk.OptionMenu(search_frame, self.search_type_display_var, self.search_type_display_var.get())
        menu2 = self.search_type_menu["menu"]
        menu2.delete(0, "end")
        for key in Download_page_search.search_types.keys():
            label = _(key)
            menu2.add_command(label=label, command=lambda k=key, l=label: (self.search_type_var.set(k), self.search_type_display_var.set(l)))
        self.search_type_menu.pack(side=tk.LEFT, padx=5)

        self.max_results_label = ttk.Label(search_frame, text=_("Max Results:"))
        self.max_results_label.pack(side=tk.LEFT, padx=5)

        self.max_results_entry = ttk.Entry(search_frame, width=5)
        self.max_results_entry.pack(side=tk.LEFT, padx=5)
        self.max_results_entry.insert(0, "100")

        self.search_button = ttk.Button(search_frame, text=_("Search"), command=self.start_search_thread)
        self.search_button.pack(side=tk.LEFT, padx=5)

        # Action frame
        action_frame = ttk.Frame(self)
        action_frame.pack(pady=5, padx=5, fill=tk.X)

        self.select_all_button = ttk.Button(action_frame, text=_("Select/Deselect All"), command=self.toggle_select_all)
        self.select_all_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = ttk.Button(action_frame, text=_("Clear All"), command=self.clear_all)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.clear_not_selected_button = ttk.Button(action_frame, text=_("Clear Not Selected"), command=self.clear_not_selected)
        self.clear_not_selected_button.pack(side=tk.LEFT, padx=5)

        self.download_button = ttk.Button(action_frame, text=_("Download Selected"), command=self.start_download_thread)
        self.download_button.pack(side=tk.LEFT, padx=5)

        # Results frame
        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.results_tree = ttk.Treeview(self.results_frame, columns=("check", "Title", "Size", "Link"), show="headings")
        self.results_tree.heading("check", text=_("Select"), command=lambda: self.sort_treeview("check", False))
        self.results_tree.heading("Title", text=_("Title"), command=lambda: self.sort_treeview("Title", False))
        self.results_tree.heading("Size", text=_("Size"), command=lambda: self.sort_treeview("Size", False))
        self.results_tree.heading("Link", text=_("Link"))
        self.results_tree.column("check", width=10, anchor="center")
        self.results_tree.column("Title", width=240)
        self.results_tree.column("Size", width=20)
        self.results_tree.column("Link", width=180)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.results_tree.pack(fill=tk.BOTH, expand=True)
        self.results_tree.bind("<Double-1>", self.toggle_check)

        # Log frame
        self.log_frame = ttk.Frame(self)
        self.log_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(self.log_frame, height=10, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.check_vars = []

        # Define tags for colored text
        self.log_text.tag_config("info", foreground="blue")
        self.log_text.tag_config("warning", foreground="orange")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("success", foreground="green")

    def get_check_symbol(self, checked):
        return "✓" if checked else "✗"

    def toggle_check(self, event):
        item = self.results_tree.selection()[0]
        index = int(self.results_tree.item(item, "tags")[0])
        self.check_vars[index] = not self.check_vars[index]
        self.results_tree.item(item, values=(self.get_check_symbol(self.check_vars[index]), *self.results_tree.item(item)["values"][1:]))

    def toggle_select_all(self):
        select_all = not all(self.check_vars)
        for i in range(len(self.check_vars)):
            self.check_vars[i] = select_all
            item = self.results_tree.get_children()[i]
            self.results_tree.item(item, values=(self.get_check_symbol(select_all), *self.results_tree.item(item)["values"][1:]), tags=(str(i),))

    def start_search_thread(self):
        """
        Starts the search in a separate thread for each selected source.
        Initializes a queue to collect results and starts processing the queue.
        """
        self.searching = True
        self.result_queue = queue.Queue()
        self.threads = []
        self.link_2_files = []
        self.max_results = int(self.max_results_entry.get())
        prompt = self.search_entry.get()
        file_type = self.file_type_var.get()
        search_type = self.search_type_var.get()
        selected_sources = [source["class"] for i, source in enumerate(SOURCES) if self.source_vars[i].get()]
        self.stop_event = threading.Event() 

        def search_source(source_class):
            try:
                results = source_class().search(prompt, file_type, search_type)
                for r in results:
                    if self.stop_event.is_set():
                        break
                    self.result_queue.put(r)
            except Exception as e:
                self.log(_("Error in source {}: {}").format(source_class.__name__, e), "error")

        for source_class in selected_sources:
            t = threading.Thread(target=search_source, args=(source_class,))
            t.start()
            self.threads.append(t)

        self.log(_("Search initiated..."), "info", end="")
        self.after(100, self.process_search_queue)

    def process_search_queue(self):
        """
        Processes the result queue, adding unique results to the treeview.
        Stops adding results if max_results is reached and sets the `stop_event`.
        """
        added = 0
        while not self.result_queue.empty() and (not self.max_results or len(self.link_2_files) < self.max_results):
            link_2_file = self.result_queue.get()
            self.add_unique_to_results([link_2_file])
            self.link_2_files.append(link_2_file)
            self.log(".", "info", end="")
            added += 1

            # Pokud jsme dosáhli max_results, nastav stop_event
            if self.max_results and len(self.link_2_files) >= self.max_results:
                self.stop_event.set()

        if (any(t.is_alive() for t in self.threads) or not self.result_queue.empty()) and not self.stop_event.is_set():
            self.after(100, self.process_search_queue)
        elif any(t.is_alive() for t in self.threads) or not self.result_queue.empty():
            # Po dosažení max_results ještě necháme doběhnout frontu
            self.after(100, self.process_search_queue)
        else:
            self.log(_("\nNumber of files found: {}").format(len(self.link_2_files)), "success")
            self.searching = False

    def start_download_thread(self):
        threading.Thread(target=self.download_selected, daemon=True).start()
    
    def download_worker(self, q: queue.Queue, timeout: int, success_list: list, success_lock: threading.Lock):
        """
        Worker function to download files from the queue.
        
        Args:
            q (queue.Queue): Queue containing Link_to_file objects to download.
            timeout (int): Timeout between downloads.
            success_list (list): Shared list to store successfully downloaded files.
            success_lock (threading.Lock): Lock to synchronize access to success_list.
        """
        while not q.empty():
            link_2_file = q.get()

            # test if file exists
            target_path = f"{download_folder}/{link_2_file.title}"
            if os.path.exists(target_path):
                self.log(_("File {} already exists.").format(link_2_file.title), "warning")
                with success_lock:
                    success_list.append(link_2_file)
                continue

            self.log(_("Downloading file: {} of size {}...").format(link_2_file.title, link_2_file.size), "info")

            try:
                link_2_file.download(download_folder)

                file_size = os.path.getsize(target_path)
                if link_2_file.source_class.test_downloaded_file(link_2_file, download_folder):
                    with success_lock:
                        success_list.append(link_2_file)
                    self.log(_("File {} of size {} was downloaded.").format(link_2_file.title, size_int_2_string(file_size)), "success")
                    self.remove_from_results([link_2_file])
            except ValueError as e:
                self.log(_("Error: {}").format(e), "error")
                self.log(_("File {} was not downloaded correctly.").format(link_2_file.title), "error")
                if os.path.exists(target_path):
                    os.remove(target_path)
                    self.log(_("File {} was removed.").format(link_2_file.title), "info")
            except InsufficientTimeoutError as e:
                self.log(_("Error: {}").format(e), "error")
                self.log(_("File {} was not downloaded at all.").format(link_2_file.title), "error")
                if os.path.exists(target_path):
                    os.remove(target_path)
                    self.log(_("File {} was removed.").format(link_2_file.title), "info")
                if self.add_files_with_failed_timeout_var.get():
                    q.put(link_2_file)
                    self.log(_("File {} was added back to the list.").format(link_2_file.title), "info")
            except Exception as e:
                self.log(_("Error: {}").format(e), "error")
                if os.path.exists(target_path):
                    os.remove(target_path)
                    self.log(_("File {} was removed.").format(link_2_file.title), "info")

            time.sleep(timeout)

    def download_selected(self):
        """
        Downloads all selected `Link_to_file` objects using worker threads.

        1. loads selected `Link_to_file` objects,
        2. groups them by `source_class`,
        3. starts a worker thread for each group to download files with appropriate timeout,
        4. waits for all threads to complete,
        5. removes successfully downloaded files from the results and JSON file if configured.

        """
        self.log(_("Download initiated..."), "info")

        selected = self.get_selected_link_2_files()
        if not selected:
            self.log(_("No files selected for download."), "warning")
            return

        self.log(_("Number of files to download: {}").format(len(selected)), "info")

        # Seskupit podle source_class
        groups: dict = {}
        for l in selected:
            groups.setdefault(l.source_class, []).append(l)

        threads = []
        successfull_files: list = []
        success_lock = threading.Lock()

        for source_class, items in groups.items():
            q = queue.Queue()
            for it in items:
                q.put(it)

            # najít timeout pro daný zdroj
            timeout = next((s["timeout"] for s in SOURCES if s["class"] == source_class), TIME_OUT)

            t = threading.Thread(target=self.download_worker, args=(q, timeout, successfull_files, success_lock), daemon=True)
            t.start()
            threads.append(t)

        # počkat na dokončení všech worker vláken
        for t in threads:
            t.join()

        self.log(_("Downloaded files: {}").format(len(successfull_files)), "success")

        if self.remove_successful_var.get():
            self.log(_("Removing successful downloads from the list..."), "info")
            remove_links_from_file(successfull_files, JSON_FILE)

    def result_tree_2_link_2_files(self):
        """
        Yields Link_to_file objects from the results treeview.
        """
        for item in self.results_tree.get_children():
            check, title, size, link = self.results_tree.item(item)["values"]
            l2f = self.link_map.get(link)
            if l2f is not None:
                yield l2f
            else:
                self.log(_("Warning: Link not found in map, creating new Link_to_file object."), "warning")
                yield Link_to_file(title, link, size, Download_page_search) # Fallback, should not happen

    def replace_results(self, link_2_files):
        """
        Replaces all items in the results treeview with new Link_to_file objects.
        And updates the link_map accordingly.
        """
        self.results_tree.delete(*self.results_tree.get_children())
        self.check_vars = [False for _ in link_2_files]
        self.link_map.clear()
        for i, link_2_file in enumerate(link_2_files):
            self.results_tree.insert(
                "", "end",
                values=(self.get_check_symbol(False), link_2_file.title, link_2_file.size, link_2_file.detail_url),
                tags=(str(i),)
            )
            self.link_map[link_2_file.detail_url] = link_2_file

    def add_unique_to_results(self, link_2_files):
        """
        Adds only unique Link_to_file objects to the results treeview.
        And updates the link_map accordingly.
        """
        existing_links = set(self.link_map.keys())
        for link_2_file in link_2_files:
            if link_2_file.detail_url not in existing_links:
                self.results_tree.insert(
                    "", "end",
                    values=(self.get_check_symbol(False), link_2_file.title, link_2_file.size, link_2_file.detail_url),
                    tags=(str(len(self.check_vars)),)
                )
                self.check_vars.append(False)
                self.link_map[link_2_file.detail_url] = link_2_file
                existing_links.add(link_2_file.detail_url)

    def remove_from_results(self, link_2_files):
        links_to_remove = {l.detail_url for l in link_2_files}
        for item in self.results_tree.get_children():
            _, title, size, link = self.results_tree.item(item)["values"]
            if link in links_to_remove:
                self.results_tree.delete(item)
                self.link_map.pop(link, None)

    def get_selected_link_2_files(self) -> list[Link_to_file]:
        """
        Returns a list of Link_to_file objects corresponding to currently checked items in the results treeview.
        If a selected link is missing from link_map, creates a safe fallback Link_to_file object.
        """
        selected_links = []
        # guard access to self.check_vars in case of mismatch between treeview children and check_vars length
        for i, item in enumerate(self.results_tree.get_children()):
            if i < len(self.check_vars) and self.check_vars[i]:
                try:
                    link = self.results_tree.item(item)["values"][3]
                except Exception:
                    continue
                selected_links.append(link)

        result = []
        for link in selected_links:
            l2f = self.link_map.get(link)
            if l2f is None:
                # Fallback: create a minimal Link_to_file object if map is missing entry
                # Use link as title and unknown size; Download_page_search as a neutral source_class
                self.log(_("Warning: Selected link {} not found in map, creating fallback object.").format(link), "warning")
                try:
                    fallback = Link_to_file(link, link, "unknown", Download_page_search)
                    result.append(fallback)
                except Exception:
                    # If construction fails, skip the entry
                    self.log(_("Failed to create fallback for {}").format(link), "error")
            else:
                result.append(l2f)
        return result

    def save_selected(self):
        """
        Loads selected items from the results treeview.
        Maps them to Link_to_file objects using link_map.
        Saves the Link_to_file objects to JSON_FILE.
        """
        self.log(_("Saving selected items..."), "info")

        link_2_files = self.get_selected_link_2_files()
        save_links_to_file(link_2_files, JSON_FILE)

        self.log(_("Saved items: {}").format(len(link_2_files)), "success")

    def load_from_file(self):
        self.log(_("Loading selected items..."), "info")
        link_2_files = load_links_from_file(JSON_FILE)
        self.replace_results(link_2_files) # automatically updates link_map
        self.log(_("Loaded items: {}").format(len(link_2_files)), "success")

    def clear_all(self):
        """
        Clears all items from the:
         - results treeview,
         - link_map.
        """
        self.results_tree.delete(*self.results_tree.get_children())
        self.check_vars = []
        self.link_map.clear()
        self.log(_("Cleared all displayed files."), "info")

    def clear_not_selected(self):
        items_to_keep = [(self.results_tree.item(item)["values"], self.results_tree.item(item)["tags"]) for i, item in enumerate(self.results_tree.get_children()) if self.check_vars[i]]
        self.results_tree.delete(*self.results_tree.get_children())
        self.check_vars = [True for _ in items_to_keep]
        for values, tags in items_to_keep:
            self.results_tree.insert("", "end", values=values, tags=tags)
        self.log(_("Cleared not selected files."), "info")

    def log(self, message, tag="info", end="\n"):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + end, tag)
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)

    def sort_treeview(self, col, reverse):
        items = [(self.results_tree.set(k, col), k) for k in self.results_tree.get_children('')]
        if col == "Size":
            items.sort(key=lambda t: size_string_2_bytes(t[0]), reverse=reverse)
        elif col == "check":
            items.sort(key=lambda t: self.check_vars[int(self.results_tree.item(t[1], "tags")[0])], reverse=reverse)
        else:
            items.sort(reverse=reverse)
        
        for index, (val, k) in enumerate(items):
            self.results_tree.move(k, '', index)
        
        self.results_tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))

    def change_language(self, *args):
        self.setup_translation()
        self.update_ui_texts()
        self.settings["language"] = self.current_language.get()
        self.save_config()

    def update_remove_successful(self, *args):
        self.settings["remove_successful"] = self.remove_successful_var.get()
        self.save_config()
    
    def update_add_files_with_failed_timeout(self, *args):
        self.settings["add_files_with_failed_timeout"] = self.add_files_with_failed_timeout_var.get()
        self.save_config()

    def update_ui_texts(self):
        self.title(_("Universal Downloader"))

        self.search_label.config(text=_("Search:"))
        self.search_button.config(text=_("Search"))
        self.max_results_label.config(text=_("Max Results:"))

        self.download_button.config(text=_("Download Selected"))
        self.clear_button.config(text=_("Clear All"))
        self.clear_not_selected_button.config(text=_("Clear Not Selected"))
        self.select_all_button.config(text=_("Select/Deselect All"))

        self.results_tree.heading("check", text=_("Select"))
        self.results_tree.heading("Title", text=_("Title"))
        self.results_tree.heading("Size", text=_("Size"))
        self.results_tree.heading("Link", text=_("Link"))
        self._rebuild_type_menus()
        self.log(_("Language changed to {}.").format(self.current_language.get()), "info")

    def _rebuild_type_menus(self):
        # rebuild file type menu
        try:
            menu = self.file_type_menu["menu"]
            menu.delete(0, "end")
            for key in Download_page_search.file_types.keys():
                label = _(key)
                menu.add_command(label=label, command=lambda k=key, l=label: (self.file_type_var.set(k), self.file_type_display_var.set(l)))
            # update displayed label to translated value for current key
            self.file_type_display_var.set(_(self.file_type_var.get()))
        except Exception:
            print_error("Error rebuilding {Blue}file type{NC} menus.")
            pass

        # rebuild search type menu
        try:
            menu2 = self.search_type_menu["menu"]
            menu2.delete(0, "end")
            for key in Download_page_search.search_types.keys():
                label = _(key)
                menu2.add_command(label=label, command=lambda k=key, l=label: (self.search_type_var.set(k), self.search_type_display_var.set(l)))
            self.search_type_display_var.set(_(self.search_type_var.get()))
        except Exception:
            print_error("Error rebuilding {Blue}search type{NC} menus.")
            pass

def main():
    if not os.path.exists(JSON_FILE):
        open(JSON_FILE, 'w').close()
        print_info(f"Created empty JSON file at {JSON_FILE}")
    
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
        print_info(f"Created download folder at {download_folder}")
    
    compile_mo_files()
    localedir = get_resource_path("locales")
    if not os.path.exists(os.path.join(localedir, "cs", "LC_MESSAGES", DOMAIN + ".mo")):
        print_error("Translation file not found!")
    
    app = DownloaderGUI()
    app.mainloop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download files from internet.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode.")
    parser.add_argument("-D", "--debug", action="store_true", help="Debug mode.")
    args = parser.parse_args()

    main()
