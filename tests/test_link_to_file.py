import pytest
import os

from main import *
from link_to_file import Link_to_file


@pytest.mark.parametrize("lines, link_2_files", [
    (
        """
{"title": "Karel \u010capek - Apokryfy (2008).mp3", "link": "https://sdilej.cz/free/index.php?id=28238129", "size": "114.4 MB"}
{"title": "MLUVEN\u00c9 SLOVO \u010capek, Karel Tov\u00e1rna na absolutno.mp3", "link": "https://sdilej.cz/free/index.php?id=29079872", "size": "175.2 MB"}
{"title": "MLUVENE SLOVO Capek Karel Tovarna na absolutno.mp3", "link": "https://sdilej.cz/free/index.php?id=29271736", "size": "175.2 MB"}

""",
        (
            None,
            Link_to_file("Karel Čapek - Apokryfy (2008).mp3", "https://sdilej.cz/free/index.php?id=28238129", "114.4 MB"),
            Link_to_file("MLUVENÉ SLOVO Čapek, Karel Továrna na absolutno.mp3", "https://sdilej.cz/free/index.php?id=29079872", "175.2 MB"),
            Link_to_file("MLUVENE SLOVO Capek Karel Tovarna na absolutno.mp3", "https://sdilej.cz/free/index.php?id=29271736", "175.2 MB"),
            None
        )
    )
])
def test_from_json(lines, link_2_files):
    link_2_file = Link_to_file("title", "link", "size")
    print(lines)
    for i, line in enumerate(lines.split("\n")):
        print("Index:", i)
        print("Line:", line)
        if line == "":
            continue
        link_2_file = link_2_file.from_json(line)
        
        assert str(link_2_file) == str(link_2_files[i])
        assert link_2_file == link_2_files[i]
        
def test_server_name():
    link_2_file = Link_to_file("title", "https://sdilej.cz/free/index.php?id=28238129", "size")
    assert link_2_file.server_name() == "sdilej.cz"

@pytest.mark.parametrize("size, value", [
    ("2.8 GB", 2.8*1024*1024*1024),
    ("2.8 MB", 2.8*1024*1024),
    ("2.8 KB", 2.8*1024),
    ("2.8 B", 2.8),
    ("2.8 ", 2.8)
])
def test_size_string_2_bytes(size, value):
    assert size_string_2_bytes(size) == int(value)

@pytest.mark.parametrize("title, link, size", [(
    "Zaklínač - Bouřková sezóna.epub",
    "https://sdilej.cz/free/index.php?id=27818824",
    "2.8 MB"
)]
)
def test_download(title, link, size):
    link_2_file = Link_to_file(title, link, size)
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
        
        # Ensure the file is deleted
        assert not os.path.exists(file_path)