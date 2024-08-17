import pytest

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