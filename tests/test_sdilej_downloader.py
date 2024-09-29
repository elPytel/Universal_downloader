import pytest

from main import *
from link_to_file import Link_to_file
from sdilej_downloader import *


@pytest.mark.parametrize("page, link_2_file", [
    (
"""
<div class="videobox-desc">
<p class="videobox-title"><a href="https://toplinktracker.com/?x=f4901bb6fb15cbafd69eeefexcwyexxf7a27ab08d4bcabtyiiyetybba38bc4d48ed59c9e12ec49182&amp;y=a3ea680a4eab4eaa45b24a4464f71ba1b404f845c72e86a6" title="Pratchett, Terry - Uzasna Zemeplocha 05 - Magicky prazdroj - (Audiokniha) rar">Pratchett, Terry   Uzasna...azdroj   (Audiokniha) rar</a></p>
<p>682MB</p>
</div>
""",
        Link_to_file("Pratchett, Terry - Uzasna Zemeplocha 05 - Magicky prazdroj - (Audiokniha) rar", "https://toplinktracker.com/?x=f4901bb6fb15cbafd69eeefexcwyexxf7a27ab08d4bcabtyiiyetybba38bc4d48ed59c9e12ec49182&y=a3ea680a4eab4eaa45b24a4464f71ba1b404f845c72e86a6", "682MB"))
])
def test_get_atributes_from_catalogue(page, link_2_file):
    soup = bs4.BeautifulSoup(page, "html.parser")
    assert str(get_atributes_from_catalogue(soup)) == str(link_2_file)


@pytest.mark.parametrize("page, link_2_file", [
    (
        """
<h1 style="font-size:23px">christie agatha - krysy.mp3</h1>
<b>Velikost:</b> 63.3 MB <br/>
<a class="btn btn-danger" href="/free/index.php?id=11038881" onclick="showModalForFreeUsers();;countFbSlow();">Stáhnout zdarma</a>
""",
        (Link_to_file("christie agatha - krysy.mp3", "https://sdilej.cz/free/index.php?id=11038881", "63.3 MB")))
])
def test_get_atributes_from_file_page(page, link_2_file):
    soup = bs4.BeautifulSoup(page, "html.parser")
    assert str(get_atributes_from_file_page(soup)) == str(link_2_file)


@pytest.mark.parametrize("link_2_file", [
    (Link_to_file("Sergey Nevone &", "https://toplinktracker.com/?x=8db963822a1a9a41d02d453eycyrxby9eb2f1aab920b1ctyiibhhmyh1bde26920e9896507d1c738bf&y=5fa464601cc3c8a488451222d1d4660f91aa93cb114187a3", "0 / Délka: /img/transparent.png"))
])
def test_get_atributes_from_file_page_exception(link_2_file):
    with pytest.raises(ValueError):
        download_page_content = parse_file_page(download_page(link_2_file.link))
        get_atributes_from_file_page(download_page_content)


@pytest.mark.parametrize("prompt, file_type, url", [
    ("zemeplocha", "archive", "https://sdilej.cz/zemeplocha/s/archive-"),
])
def test_search(prompt, file_type, url):
    assert Sdilej_downloader.generate_search_url(prompt, file_type) == url


@pytest.mark.parametrize("url, validity", [
    ("https://toplinktracker.com/?x=5ef00a5ea7e01f03ef7bee4ggcdnnngdbb0154dd525b79tyiibeebyh2cbadfada495d81f3d7a9b0d2&y=b797ef823c50c33f7a2f8046fe94d9bffa3b07158b5c847c", False),
    ("https://toplinktracker.com/?x=af4baeedcfed92686a83bf1bxdrcdd709648e7d21b782tyiibhhehd8d20f43f7d764d7e032ba2f18&y=cf7643e4e82d5a9865ea5fb3db4940cba29efd08d6698bf4", False)
])
def test_is_valid_download_page(url, validity):
    page = download_page(url)
    print("Status code:", page.status_code)
    assert is_valid_download_page(page) == validity
