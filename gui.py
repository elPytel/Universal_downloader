import tkinter as tk
from tkinter import ttk
from link_to_file import *
from sdilej_downloader import Sdilej_downloader

class DownloaderGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Universal Downloader")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        search_frame = ttk.Frame(self)
        search_frame.pack(pady=5, padx=5, fill=tk.X)

        self.search_label = ttk.Label(search_frame, text="Search:")
        self.search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.file_type_var = tk.StringVar(value="all")
        self.file_type_menu = ttk.OptionMenu(search_frame, self.file_type_var, "all", *Sdilej_downloader.file_types.keys())
        self.file_type_menu.pack(side=tk.LEFT, padx=5)

        self.search_type_var = tk.StringVar(value="relevance")
        self.search_type_menu = ttk.OptionMenu(search_frame, self.search_type_var, "relevance", *Sdilej_downloader.search_types.keys())
        self.search_type_menu.pack(side=tk.LEFT, padx=5)

        self.search_button = ttk.Button(search_frame, text="Search", command=self.search_files)
        self.search_button.pack(side=tk.LEFT, padx=5)

        self.download_button = ttk.Button(search_frame, text="Download Selected", command=self.download_selected)
        self.download_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(search_frame, text="Save Selected", command=self.save_selected)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.load_button = ttk.Button(search_frame, text="Load Selected", command=self.load_selected)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.results_tree = ttk.Treeview(self.results_frame, columns=("Select", "Title", "Size", "Link"), show="headings")
        self.results_tree.heading("Select", text="Select")
        self.results_tree.heading("Title", text="Title")
        self.results_tree.heading("Size", text="Size")
        self.results_tree.heading("Link", text="Link")
        self.results_tree.pack(fill=tk.BOTH, expand=True)

        self.log_frame = ttk.Frame(self)
        self.log_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(self.log_frame, height=10, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def search_files(self):
        self.log("Search initiated...")
        prompt = self.search_entry.get()
        file_type = self.file_type_var.get()
        search_type = self.search_type_var.get()
        
        link_2_files = Sdilej_downloader().search(prompt, file_type, search_type)
        self.log(f"Number of files found: {len(link_2_files)}")
        
        for link_2_file in link_2_files:
            self.results_tree.insert("", "end", values=(False, link_2_file.title, link_2_file.size, link_2_file.link))

    def download_selected(self):
        self.log("Download initiated...")
        selected_items = [self.results_tree.item(item)["values"] for item in self.results_tree.get_children() if self.results_tree.item(item)["values"][0]]
        self.log(f"Selected items for download: {selected_items}")
        
        if not os.path.exists(JSON_FILE):
            save_links_to_file(selected_items, JSON_FILE)
        else:
            add_links_to_file(selected_items, JSON_FILE)

    def save_selected(self):
        self.log("Saving selected items...")

        # get selected items
        selected_items = [self.results_tree.item(item)["values"] for item in self.results_tree.get_children() if self.results_tree.item(item)["values"][0]]
        
        # get links
        link_2_files = [ Link_to_file(title, link, size) for _, title, size, link in selected_items]
        save_links_to_file(link_2_files, JSON_FILE)
        
        self.log(f"Saved items: {len(link_2_files)}")

    def load_selected(self):
        self.log("Loading selected items...")
        link_2_files = load_links_from_file(JSON_FILE)
        self.results_tree.delete(*self.results_tree.get_children())
        for link_2_file in link_2_files:
            self.results_tree.insert("", "end", values=(False, link_2_file.title, link_2_file.size, link_2_file.link))
        self.log(f"Loaded items: {link_2_files}")

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)

def main():
    app = DownloaderGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
