import pytest

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bs4
import re
from src.link_to_file import Link_to_file
from src.downloader.page_search import *

page = """
<ul class="list list--description word-break">
    <li> <span class="color-primary">Název souboru:</span> <span>Krteček 33</span> </li>
    <li> <span class="color-primary">Velikost:</span> <span>51.28 MB</span> </li>
    <li> <span class="color-primary">Datum nahrání:</span> <span>2025-01-29 16:38:10</span> </li>
    <li> <span class="color-primary">Délka:</span> <span>00:05:19</span> </li>
    <li> <span class="color-primary">Formát:</span> <span>avi</span> </li>
</ul>
"""

@pytest.mark.parametrize("page, label, expected_output, value", [
    (page, "Název souboru", "<span class=\"color-primary\">Název souboru:</span>", "Krteček 33"),
    (page, "Velikost", "<span class=\"color-primary\">Velikost:</span>", "51.28 MB"),
    (page, "Datum nahrání", "<span class=\"color-primary\">Datum nahrání:</span>", "2025-01-29 16:38:10"),
    (page, "Délka", "<span class=\"color-primary\">Délka:</span>", "00:05:19"),
    (page, "Formát", "<span class=\"color-primary\">Formát:</span>", "avi")
])
def test_find_label_span_and_extract_value(page, label, expected_output, value):
    soup = bs4.BeautifulSoup(page, "html.parser")
    result_label = find_label_span_by_regex(soup, rf'^\s*{re.escape(label)}[:\s]*$')
    print("Found span:", result_label)
    assert str(result_label) == expected_output
    result = extract_value_from_label(result_label)
    print("Extracted value:", result)
    assert result == value