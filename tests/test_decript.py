import os
import sys
import pytest

# Ensure project root is on sys.path so `src` can be imported as a namespace package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.decript import datoid_decrypt

@pytest.mark.parametrize("data_href, title, expected", [
    ("kZLktdDB", "bones-s04e04-avi", 'm0uGkN'),
    ("l8few9+k", "bones-s02e16-avi", 'seoUz1'),
    ("Z5fbwNW/", "bones-s02e20-avi", 'C5lRpL'),
])
def test_known_decryptions(data_href, title, expected):
    assert datoid_decrypt(data_href, title) == expected

def test_invalid_base64_returns_empty():
    assert datoid_decrypt("not_base64!!", "title") == ""
