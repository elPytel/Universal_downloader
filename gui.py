import tkinter as tk
from tkinter import ttk
from link_to_file import load_links_from_file, JSON_FILE

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

        self.search_button = ttk.Button(search_frame, text="Search", command=self.search_files)
        self.search_button.pack(side=tk.LEFT, padx=5)

        self.download_button = ttk.Button(search_frame, text="Download Selected", command=self.download_selected)
        self.download_button.pack(side=tk.LEFT, padx=5)

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
        # Implement search logic here
        self.log("Search initiated...")
        # Example of adding search results with checkboxes
        for i in range(5):  # Replace with actual search results
            self.results_tree.insert("", "end", values=(False, f"Title {i}", f"Size {i}", f"Link {i}"))

    def download_selected(self):
        # Implement download logic here
        self.log("Download initiated...")
        selected_items = [self.results_tree.item(item)["values"] for item in self.results_tree.get_children() if self.results_tree.item(item)["values"][0]]
        self.log(f"Selected items for download: {selected_items}")

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
