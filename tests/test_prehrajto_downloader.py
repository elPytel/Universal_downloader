import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import bs4
from src.link_to_file import Link_to_file
from src.downloader.prehrajto import *

# obsah stránky s výsledky hledání
"""
<div class="grid-x small-up-2 large-up-3 grid-margin-x grid-margin-y align-center-small">
    <div>
        <div class="video__picture--container"> <a class="video video--small video--link"
                href="/krtecek-na-pousti/67c6ca3b557ac" title="Krteček na pousti">
                <div class="video__header">
                    <picture class="video-item-thumb video__picture"> <img data-next="2" class="thumb thumb1"
                            src="https://thumb.prehrajto.cz/6/7/c/6/c/a//67c6ca3b557ac//1.jpg" width="214" height="120"
                            style="display: inline-block;"> </picture>
                    <div class="video__tag video__tag--time">00:05:35</div>
                    <div class="video__tag video__tag--size">20.02 MB</div> <span class="video__play"> <svg class="icon"
                            role="presentation" width="20" height="20">
                            <use xlink:href="/front/img/sprite/sprite.svg#sprite-play"></use>
                        </svg> </span>
                </div>
                <div class="video__content text-center large-text-left">
                    <h3 class="video__title margin-bottom-0">Krteček na pousti</h3>
                </div>
            </a> </div>
    </div>
    <div>
        <div class="video__picture--container"> <a class="video video--small video--link"
                href="/krtecek-krtek-a-zvykacka/609d6777172e0" title="krtecek-krtek-a-zvykacka">
                <div class="video__header">
                    <picture class="video-item-thumb video__picture"> <img data-next="2" class="thumb thumb1"
                            src="https://thumb.prehrajto.cz/6/0/9/d/6/7//609d6777172e0//1.jpg" width="214" height="120"
                            style="display: inline-block;"> </picture>
                    <div class="video__tag video__tag--time">00:07:26</div>
                    <div class="video__tag video__tag--size">70.79 MB</div> <span class="video__play"> <svg class="icon"
                            role="presentation" width="20" height="20">
                            <use xlink:href="/front/img/sprite/sprite.svg#sprite-play"></use>
                        </svg> </span>
                </div>
                <div class="video__content text-center large-text-left">
                    <h3 class="video__title margin-bottom-0">krtecek-krtek-a-zvykacka</h3>
                </div>
            </a> </div>
    </div>
    <div>
        <div class="video__picture--container"> <a class="video video--small video--link"
                href="/krtecek-krtek-a-televizor/609d67ce161fb" title="Krteček-Krtek-a-televizor">
                <div class="video__header">
                    <picture class="video-item-thumb video__picture"> <img data-next="2" class="thumb thumb1"
                            src="https://thumb.prehrajto.cz/6/0/9/d/6/7//609d67ce161fb//1.jpg" width="214" height="120"
                            style="display: inline-block;"> 
                    </picture>
                    <div class="video__tag video__tag--time">00:05:30</div>
                    <div class="video__tag video__tag--size">52.02 MB</div> <span class="video__play"> <svg class="icon"
                            role="presentation" width="20" height="20">
                            <use xlink:href="/front/img/sprite/sprite.svg#sprite-play"></use>
                        </svg> </span>
                </div>
                <div class="video__content text-center large-text-left">
                    <h3 class="video__title margin-bottom-0">Krteček-Krtek-a-televizor</h3>
                </div>
            </a> </div>
    </div>
"""

@pytest.mark.parametrize("page, link_2_file", [
    (
"""
<a class="video video--small video--link" href="/krtecek-33/679a4b625fc58" title="Krteček 33">
    <div class="video__header">
        <picture class="video-item-thumb video__picture"> <img data-next="2" class="thumb thumb1"
                src="https://thumb.prehrajto.cz/6/7/9/a/4/b//679a4b625fc58//1.jpg" width="214" height="120"
                style="display: inline-block;">
        </picture>
        <div class="video__tag video__tag--time">00:05:19</div>
        <div class="video__tag video__tag--size">51.28 MB</div> <span class="video__play"> <svg class="icon"
                role="presentation" width="20" height="20">
                <use xlink:href="/front/img/sprite/sprite.svg#sprite-play"></use>
            </svg> </span>
    </div>
    <div class="video__content text-center large-text-left">
        <h3 class="video__title margin-bottom-0">Krteček 33</h3>
    </div>
</a>
""",
        Link_to_file("Krteček 33", "https://prehraj.to/krtecek-33/679a4b625fc58", "51.28 MB", Prehrajto_downloader))
])
def test_get_atributes_from_catalogue(page, link_2_file):
    soup = bs4.BeautifulSoup(page, "html.parser")
    assert str(Prehrajto_downloader.get_atributes_from_catalogue(soup)) == str(link_2_file)

@pytest.mark.parametrize("url, download_link", [
    ("https://prehraj.to/krtecek-33/679a4b625fc58", "https://prehraj.to/krtecek-33/679a4b625fc58?do=download")
])
def test_get_download_link(url, download_link):
    link_2_file = Link_to_file("Test", url, "Test", Prehrajto_downloader)
    assert link_2_file.get_download_link() == download_link

@pytest.mark.parametrize("prompt, file_type, url", [
    ("krteček", "video", "https://prehraj.to/hledej/krteček"),
    ("karel čapek", "video", "https://prehraj.to/hledej/karel%20čapek"),
    ("zaklínač", "all", "https://prehraj.to/hledej/zaklínač"),
])
def test_search(prompt, file_type, url):
    assert Prehrajto_downloader.generate_search_url(prompt, file_type) == url