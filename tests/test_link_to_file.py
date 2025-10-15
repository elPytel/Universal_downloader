import pytest

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import *
from link_to_file import Link_to_file
from sdilej_downloader import Sdilej_downloader


@pytest.mark.parametrize("lines, link_2_files", [
    (
        """
{"title": "Karel \u010capek - Apokryfy (2008).mp3", "detail_url": "https://sdilej.cz/free/index.php?id=28238129", "size": "114.4 MB", "source_class": "Sdilej_downloader"}
{"title": "MLUVEN\u00c9 SLOVO \u010capek, Karel Tov\u00e1rna na absolutno.mp3", "detail_url": "https://sdilej.cz/free/index.php?id=29079872", "size": "175.2 MB", "source_class": "Sdilej_downloader"}
{"title": "MLUVENE SLOVO Capek Karel Tovarna na absolutno.mp3", "detail_url": "https://sdilej.cz/free/index.php?id=29271736", "size": "175.2 MB", "source_class": "Sdilej_downloader"}

""",
        (
            None,
            Link_to_file("Karel Čapek - Apokryfy (2008).mp3", "https://sdilej.cz/free/index.php?id=28238129", "114.4 MB", Sdilej_downloader),
            Link_to_file("MLUVENÉ SLOVO Čapek, Karel Továrna na absolutno.mp3", "https://sdilej.cz/free/index.php?id=29079872", "175.2 MB", Sdilej_downloader),
            Link_to_file("MLUVENE SLOVO Capek Karel Tovarna na absolutno.mp3", "https://sdilej.cz/free/index.php?id=29271736", "175.2 MB", Sdilej_downloader),
            None
        )
    )
])
def test_from_json(lines, link_2_files):
    link_2_file = Link_to_file("title", "detail_url", "size", Sdilej_downloader)
    print(lines)
    for i, line in enumerate(lines.split("\n")):
        print("Index:", i)
        print("Line:", line)
        if line == "":
            continue
        link_2_file = link_2_file.from_json(line)
        
        assert str(link_2_file) == str(link_2_files[i])
        assert link_2_file == link_2_files[i]

@pytest.mark.parametrize("file, ext", [
    ("file.txt", ".txt"),
    ("file.tar.gz", ".gz"),
    ("file", None),
    ("file.", "."),
    ("text.avi", ".avi"),
    ("file.name.with.dots.mp3", ".mp3"),
    ("file.name.with.dots", ".dots"),
    ("file.name.with.dots.", "."),
    ("Karel Čapek - Apokryfy (2008).mp3", ".mp3"),
    ("MLUVENÉ SLOVO Čapek, Karel Továrna na absolutno.mp3", ".mp3")
])
def test_get_extension_from_title(file, ext):
    assert get_extension_from_title(file) == ext

@pytest.mark.parametrize("url, ext", [
    ("https://example.com/file.txt", ".txt"),
    ("https://example.com/file.tar.gz", ".gz"),
    ("https://example.com/file", None),
    ("https://example.com/file.", "."),
    ("https://example.com/text.avi", ".avi"),
    ("https://example.com/file.name.with.dots.mp3", ".mp3"),
    ("https://example.com/file.name.with.dots", ".dots"),
    ("https://example.com/file.name.with.dots.", ".")
])
def test_get_extension_from_url(url, ext):
    assert get_extension_from_url(url) == ext

@pytest.mark.parametrize("link_2_file", [
    Link_to_file("title", "detail_url", "size", Sdilej_downloader)
])
def test_to_json_and_back(link_2_file):
    json_str = link_2_file.to_json()
    new_link_2_file = Link_to_file.from_json(json_str)
    assert link_2_file == new_link_2_file
        
# test new_link_2_files = list(set(old_link_2_files + links_to_add_to_file))
@pytest.mark.parametrize("old_links, new_links, result", [
    (
        [
            Link_to_file("A", "link", "size", Sdilej_downloader),
            Link_to_file("title", "link", "size", Sdilej_downloader),
            Link_to_file("title", "link", "size", Sdilej_downloader)
        ],
        [
            Link_to_file("B", "link", "size", Sdilej_downloader),
            Link_to_file("title", "link", "size", Sdilej_downloader),
            Link_to_file("title", "link", "size", Sdilej_downloader)
        ],
        [
            Link_to_file("A", "link", "size", Sdilej_downloader),
            Link_to_file("B", "link", "size", Sdilej_downloader),
            Link_to_file("title", "link", "size", Sdilej_downloader)
        ]
    )
])
def test_add_links_to_list(old_links, new_links, result):
    new_links = add_links_to_list(old_links, new_links)
    result = list(set(result))
    assert len(new_links) == len(result)
    assert set(new_links) == set(result)

def test_server_name():
    link_2_file = Link_to_file("title", "https://sdilej.cz/free/index.php?id=28238129", "size", Sdilej_downloader)
    assert link_2_file.server_name() == "sdilej.cz"

@pytest.mark.parametrize("size, value", [
    ("2.8 GB", 2.8*1024*1024*1024),
    ("2.8 MB", 2.8*1024*1024),
    ("2.8 KB", 2.8*1024),
    ("2.8 B", 2.8),
    ("2.8 ", 2.8),
    ("27.8 MB ", 27.8*1024*1024)
])
def test_size_string_2_bytes(size, value):
    assert size_string_2_bytes(size) == int(value)

@pytest.mark.parametrize("title, link, size", [(
    "Zaklínač - Bouřková sezóna.epub",
    "https://sdilej.cz/475839ed65e892d43155f468bd300c941c4c6399830d4c4f526fba957677b4e3499a938208aef7894a384d7531ae66db1ee1112e564be798b8da6ade9a11ede258901ef2",
    "2.8 MB"
)]
)
def test_download(title, link, size):
    link_2_file = Link_to_file(title, link, size, Sdilej_downloader)
    download_folder = "download"
    
    # Ensure the download folder exists
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    file_path = os.path.join(download_folder, title)
    
    try:
        # Download the file
        link_2_file.download(download_folder)
        
        # Check if the file exists
        assert os.path.exists(file_path)

        # Check if the file is not empty
        file_size = os.path.getsize(file_path)
        assert file_size > 0

        print("File size:", file_size)
        print("Link size:", link_2_file.size)
        assert compare_sizes(file_size, link_2_file.size, 20/100)
    finally:
        # Clean up: remove the downloaded file
        if os.path.exists(file_path):
            os.remove(file_path)