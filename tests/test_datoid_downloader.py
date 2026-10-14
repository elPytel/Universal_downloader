import pytest
from types import SimpleNamespace
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bs4
from src.link_to_file import Link_to_file
from src.downloader.datoid import *

@pytest.mark.parametrize("page, link_2_file", [
    (
"""
<li>
		<a href="/AJSgV7/krakatit-capek-karel-epub">
		<div class="thumb file">
            <img src="/img/type/others-64.png" alt="">
                <strong>.epub</strong>
            <div class="info">
                <div class="inner">
                    <div class="column-left">
                        <span class="likes zero">0</span>
                    </div>
                    <div class="column-right">
                        <span><i class="icon-size-white"></i>230.4 kB</span>
                    </div>
                </div>
            </div>                                            
        </div>
        <p>
           <span class="filename">Krakatit - Capek, Karel.epub</span>
        </p>
    </a>
</li>
""",
        Link_to_file("Krakatit - Capek, Karel.epub", "https://datoid.cz/AJSgV7/krakatit-capek-karel-epub", "230.4 kB", Datoid_downloader))
])
def test_get_atributes_from_catalogue(page, link_2_file):
    soup = bs4.BeautifulSoup(page, "html.parser")
    assert str(Datoid_downloader.get_atributes_from_catalogue(soup)) == str(link_2_file)

@pytest.mark.parametrize("page, link_2_file", [
    (
        """
<div id="main">
            <h1>
                Krakatit - Capek, Karel.epub
            </h1>          
            <div class="thumb file">
                <div class="info">                                
					<span><i class="icon-size-extra"></i>230.44<small>KB</small></span>
                </div>
                <span class="suffix">.epub</span>
            </div>
            <div class="tabs">
</div>                <div class="tabs-content">
                    <div id="tab-parameters" class="tab">                                    

                        <table class="parameters">
                            <tbody>
                                <tr>
                                    <th>Název souboru:</th>
                                    <td>Krakatit - Capek, Karel.epub</td>
                                </tr>
                                <tr>
                                    <th>Velikost:</th>
                                    <td>230.44 kB</td>
                                </tr>
                                <tr>
                                    <th>Typ souboru:</th> 
                                    <td>.epub</td>
                                </tr>
                                <tr>
                                    <th>Titul:</th> 
                                    <td>Krakatit</td>
                                </tr>
                            </tbody>
                        </table>
                    </div> <!-- / .tab -->
            <p class="align-center">
                        <a data-code="AJSgV7" class="btn btn-large btn-download detail-download" href="/f/AJSgV7/krakatit-capek-karel-epub"><i class="icon-download-large"></i>Stáhnout</a>
            </p>
</div>
""",
        (Link_to_file("Krakatit - Capek, Karel.epub", "https://datoid.cz/f/AJSgV7/krakatit-capek-karel-epub", "230.44 kB", Datoid_downloader)))
])
def test_get_atributes_from_file_page(page, link_2_file):
    soup = bs4.BeautifulSoup(page, "html.parser")
    assert str(Datoid_downloader.get_atributes_from_file_page(soup)) == str(link_2_file)

# https://datoid.to/f/ndpuc9/bila-nemoc-capek-karel-epub?request=1
# ERROR: ip in use
"""
@pytest.mark.parametrize("url, download_link", [
    ("https://datoid.to/ndpuc9/bila-nemoc-capek-karel-epub", "TODO: actual download link here")
])
def test_get_download_link(url, download_link):
    link_2_file = Link_to_file("Test", url, "Test", Datoid_downloader)
    assert link_2_file.get_download_link() == download_link
"""

@pytest.mark.parametrize("prompt, file_type, url", [
    ("karel capek", "archive", "https://datoid.cz/s/karel-capek?key=categories&value=archive"),
])
def test_search(prompt, file_type, url):
    assert Datoid_downloader.generate_search_url(prompt, file_type) == url


def test_parse_catalogue_skips_empty_items(monkeypatch):
    page = SimpleNamespace(
        text="""
        <ul class="list" id="snippet--search_files">
            <li style="width: 100%;height: auto;"></li>
            <li>
                <a href="/AJSgV7/krakatit-capek-karel-epub">
                    <span class="filename">Krakatit - Capek, Karel.epub</span>
                    <span><i class="icon-size-white"></i>230.4 kB</span>
                </a>
            </li>
        </ul>
        """,
    )

    catalogue_file = Link_to_file(
        "Krakatit - Capek, Karel.epub",
        "https://datoid.cz/AJSgV7/krakatit-capek-karel-epub",
        "230.4 kB",
        Datoid_downloader,
    )
    monkeypatch.setattr(
        Datoid_downloader,
        "get_atributes_from_catalogue",
        staticmethod(lambda soup: catalogue_file),
    )
    monkeypatch.setattr(
        "src.downloader.datoid.download_page",
        lambda url: SimpleNamespace(text="detail page"),
    )
    monkeypatch.setattr(
        Datoid_downloader,
        "parse_file_page",
        staticmethod(lambda response: response),
    )
    monkeypatch.setattr(
        Datoid_downloader,
        "get_atributes_from_file_page",
        staticmethod(lambda soup: catalogue_file),
    )

    assert list(Datoid_downloader.parse_catalogue(page)) == [catalogue_file]


def test_get_download_links_reads_wait_and_cdn(monkeypatch):
    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "download_link": "https://s25.dynet.cz/download/token",
                "download_link_cdn": "https://s25.server2.cz/download/token",
                "wait": 30,
            }

    class FakeSession:
        def get(self, url, timeout):
            assert url.endswith("?request=1")
            return FakeResponse()

    monkeypatch.setattr("src.downloader.datoid.requests.Session", lambda: FakeSession())

    result = Datoid_downloader.get_download_links_from_detail(
        "https://datoid.cz/f/example/file"
    )

    assert result.links == [
        "https://s25.dynet.cz/download/token",
        "https://s25.server2.cz/download/token",
    ]
    assert result.wait == 30
    assert result.session is not None
