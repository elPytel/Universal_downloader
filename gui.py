import json
import gettext
import threading
import tkinter as tk
from tkinter import ttk
from link_to_file import *
from sdilej_downloader import Sdilej_downloader
from main import download_folder, JSON_FILE

CONFIG_FILE = "config.json"

class DownloaderGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.current_language = tk.StringVar(value=self.load_language())
        self.setup_translation()
        self.title(_("Universal Downloader"))
        self.geometry("800x600")
        self.create_widgets()

    def load_language(self):
        try:
            with open(CONFIG_FILE, "r") as file:
                config = json.load(file)
                return config.get("language", "cs")
        except FileNotFoundError:
            return "cs"

    def save_language(self):
        config = {"language": self.current_language.get()}
        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file)

    def setup_translation(self):
        lang_code = self.current_language.get()
        try:
            lang = gettext.translation('universal_downloader', localedir='locales', languages=[lang_code])
            lang.install()
        except Exception as e:
            print(f"Translation not found for {lang_code}, falling back to default. Error: {e}")
            gettext.install('universal_downloader', localedir='locales')
        global _
        _ = gettext.gettext

    def create_widgets(self):
        # Language selection
        lang_frame = ttk.Frame(self)
        lang_frame.pack(pady=5, padx=5, fill=tk.X)

        self.lang_label = ttk.Label(lang_frame, text=_("Language:"))
        self.lang_label.pack(side=tk.LEFT, padx=5)

        self.lang_menu = ttk.OptionMenu(lang_frame, self.current_language, self.current_language.get(), "en", "cs", command=self.change_language)
        self.lang_menu.pack(side=tk.LEFT, padx=5)

        search_frame = ttk.Frame(self)
        search_frame.pack(pady=5, padx=5, fill=tk.X)

        self.search_label = ttk.Label(search_frame, text=_("Search:"))
        self.search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.file_type_var = tk.StringVar(value="all")
        self.file_type_menu = ttk.OptionMenu(search_frame, self.file_type_var, "all", *Sdilej_downloader.file_types.keys())
        self.file_type_menu.pack(side=tk.LEFT, padx=5)

        self.search_type_var = tk.StringVar(value="relevance")
        self.search_type_menu = ttk.OptionMenu(search_frame, self.search_type_var, "relevance", *Sdilej_downloader.search_types.keys())
        self.search_type_menu.pack(side=tk.LEFT, padx=5)

        self.max_results_label = ttk.Label(search_frame, text=_("Max Results:"))
        self.max_results_label.pack(side=tk.LEFT, padx=5)

        self.max_results_entry = ttk.Entry(search_frame, width=5)
        self.max_results_entry.pack(side=tk.LEFT, padx=5)
        self.max_results_entry.insert(0, "100")  # Default value

        self.search_button = ttk.Button(search_frame, text=_("Search"), command=self.start_search_thread)
        self.search_button.pack(side=tk.LEFT, padx=5)

        action_frame = ttk.Frame(self)
        action_frame.pack(pady=5, padx=5, fill=tk.X)

        self.download_button = ttk.Button(action_frame, text=_("Download Selected"), command=self.start_download_thread)
        self.download_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(action_frame, text=_("Save Selected"), command=self.save_selected)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.load_button = ttk.Button(action_frame, text=_("Load from file"), command=self.load_selected)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.remove_successful_var = tk.BooleanVar()
        self.remove_successful_check = ttk.Checkbutton(action_frame, text=_("Remove successful from json"), variable=self.remove_successful_var)
        self.remove_successful_check.pack(side=tk.LEFT, padx=5)

        self.clear_button = ttk.Button(action_frame, text=_("Clear All"), command=self.clear_all)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        self.clear_not_selected_button = ttk.Button(action_frame, text=_("Clear Not Selected"), command=self.clear_not_selected)
        self.clear_not_selected_button.pack(side=tk.LEFT, padx=5)

        self.select_all_button = ttk.Button(action_frame, text=_("Select/Deselect All"), command=self.toggle_select_all)
        self.select_all_button.pack(side=tk.LEFT, padx=5)

        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.results_tree = ttk.Treeview(self.results_frame, columns=("check", "Title", "Size", "Link"), show="headings")
        self.results_tree.heading("check", text=_("Select"), command=lambda: self.sort_treeview("check", False))
        self.results_tree.heading("Title", text=_("Title"), command=lambda: self.sort_treeview("Title", False))
        self.results_tree.heading("Size", text=_("Size"), command=lambda: self.sort_treeview("Size", False))
        self.results_tree.heading("Link", text=_("Link"))
        self.results_tree.column("check", width=10, anchor="center")
        self.results_tree.column("Title", width=220)
        self.results_tree.column("Size", width=30)
        self.results_tree.column("Link", width=180)
        self.results_tree.pack(fill=tk.BOTH, expand=True)

        self.results_tree.bind("<Double-1>", self.toggle_check)

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
            self.results_tree.item(item, values=(self.get_check_symbol(select_all), *self.results_tree.item(item)["values"][1:]))
        self.log(_("Toggled select/deselect all."), "info")

    def start_search_thread(self):
        threading.Thread(target=self.search_files).start()

    def search_files(self):
        self.log(_("Search initiated..."), "info", end="")
        prompt = self.search_entry.get()
        file_type = self.file_type_var.get()
        search_type = self.search_type_var.get()
        max_results = int(self.max_results_entry.get())
        
        link_2_files = Sdilej_downloader().search(prompt, file_type, search_type)
        number_of_files = 0
        for i, link_2_file in enumerate(link_2_files):
            if max_results and i >= max_results:
                break
            self.check_vars.append(False)
            self.results_tree.insert("", "end", values=(self.get_check_symbol(False), link_2_file.title, link_2_file.size, link_2_file.link), tags=(str(i),))
            number_of_files = i + 1
            self.log(".", "info", end="")
        
        self.log(_("\nNumber of files found: {}").format(number_of_files), "success")

    def start_download_thread(self):
        threading.Thread(target=self.download_selected).start()

    def download_selected(self):
        self.log(_("Download initiated..."), "info")
        
        selected_items = [self.results_tree.item(item)["values"] for i, item in enumerate(self.results_tree.get_children()) if self.check_vars[i]]
        
        link_2_files = [Link_to_file(title, link, size) for _, title, size, link in selected_items]

        successfull_files = []
        for link_2_file in link_2_files:
            
            # test if file exists
            if os.path.exists(f"{download_folder}/{link_2_file.title}"):
                self.log(_("File {} already exists.").format(link_2_file.title), "warning")
                successfull_files.append(link_2_file)
                continue
            
            self.log(_("Downloading file: {} of size {}...").format(link_2_file.title, link_2_file.size), "info")

            link_2_file.download(download_folder)

            # test file size > 1kb
            file_size = os.path.getsize(f"{download_folder}/{link_2_file.title}")
            if (not compare_sizes(file_size, link_2_file.size, 20/100) and link_2_file.size != None) or (link_2_file.size == None and file_size < 1024):
                self.log(_("File {} was not downloaded correctly.").format(link_2_file.title), "error")
                self.log(_("File size: {} expected: {}").format(file_size, link_2_file.size), "error")
                os.remove(f"{download_folder}/{link_2_file.title}")
                self.log(_("File {} was removed.").format(link_2_file.title), "info")
            else:
                successfull_files.append(link_2_file)
                self.log(_("File {} of size {} was downloaded.").format(link_2_file.title, size_int_2_string(file_size)), "success")
        
        self.log(_("Downloaded files: {}").format(len(successfull_files)), "success")

        if self.remove_successful_var.get():
            self.log(_("Removing successful downloads from the list..."), "info")
            remove_links_from_file(successfull_files, JSON_FILE)

    def save_selected(self):
        self.log(_("Saving selected items..."), "info")

        selected_items = [self.results_tree.item(item)["values"] for i, item in enumerate(self.results_tree.get_children()) if self.check_vars[i]]
        
        link_2_files = [Link_to_file(title, link, size) for _, title, size, link in selected_items]
        save_links_to_file(link_2_files, JSON_FILE)
        
        self.log(_("Saved items: {}").format(len(link_2_files)), "success")

    def load_selected(self):
        self.log(_("Loading selected items..."), "info")
        link_2_files = load_links_from_file(JSON_FILE)
        self.results_tree.delete(*self.results_tree.get_children())
        self.check_vars = [False for _ in link_2_files]
        for i, link_2_file in enumerate(link_2_files):
            self.results_tree.insert("", "end", values=(self.get_check_symbol(False), link_2_file.title, link_2_file.size, link_2_file.link), tags=(str(i),))
        self.log(_("Loaded items: {}").format(len(link_2_files)), "success")

    def clear_all(self):
        self.results_tree.delete(*self.results_tree.get_children())
        self.check_vars = []
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
        self.save_language()

    def update_ui_texts(self):
        self.title(_("Universal Downloader"))
        self.search_label.config(text=_("Search:"))
        self.search_button.config(text=_("Search"))
        self.max_results_label.config(text=_("Max Results:"))
        self.download_button.config(text=_("Download Selected"))
        self.save_button.config(text=_("Save Selected"))
        self.load_button.config(text=_("Load from file"))
        self.remove_successful_check.config(text=_("Remove successful from json"))
        self.clear_button.config(text=_("Clear All"))
        self.clear_not_selected_button.config(text=_("Clear Not Selected"))
        self.select_all_button.config(text=_("Select/Deselect All"))
        self.results_tree.heading("check", text=_("Select"))
        self.results_tree.heading("Title", text=_("Title"))
        self.results_tree.heading("Size", text=_("Size"))
        self.results_tree.heading("Link", text=_("Link"))
        self.log(_("Language changed to {}.").format(self.current_language.get()), "info")

def main():
    if not os.path.exists(JSON_FILE):
        open(JSON_FILE, 'w').close()
    
    app = DownloaderGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
