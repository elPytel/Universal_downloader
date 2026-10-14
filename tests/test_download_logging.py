import logging

import pytest
import requests

from src.link_to_file import Link_to_file
from src.logging_config import configure_app_logging


class FakeSource:
    @staticmethod
    def get_download_link_from_detail(detail_url, timeout=120):
        return "https://example.test/file.bin"


class FakeResponse:
    status_code = 200
    headers = {
        "Content-Type": "application/octet-stream",
        "Content-Length": "4",
    }
    content = b"data"

    def raise_for_status(self):
        return None


def test_download_logs_success(monkeypatch, tmp_path):
    log_file = tmp_path / "download.log"
    configure_app_logging(str(log_file))
    monkeypatch.setattr("src.link_to_file.requests.get", lambda *args, **kwargs: FakeResponse())

    file = Link_to_file("file.bin", "https://example.test/detail", "4 B", FakeSource)
    file.download(str(tmp_path), timeout=10)

    assert (tmp_path / "file.bin").read_bytes() == b"data"
    log = log_file.read_text(encoding="utf-8")
    assert "Starting download" in log
    assert "Download response" in log
    assert "Download completed" in log


def test_download_logs_request_failure(monkeypatch, tmp_path):
    log_file = tmp_path / "download.log"
    configure_app_logging(str(log_file))

    def fail_request(*args, **kwargs):
        raise requests.Timeout("request timed out")

    monkeypatch.setattr("src.link_to_file.requests.get", fail_request)
    file = Link_to_file("file.bin", "https://example.test/detail", "4 B", FakeSource)

    try:
        file.download(str(tmp_path), timeout=10)
    except requests.Timeout:
        pass
    else:
        raise AssertionError("Expected requests.Timeout")

    log = log_file.read_text(encoding="utf-8")
    assert "Download failed" in log
    assert "request timed out" in log


def test_download_does_not_save_failed_fallback_response(monkeypatch, tmp_path):
    class LinkInfo:
        links = ["https://primary.example/file", "https://cdn.example/file"]
        wait = 0
        session = None

    class FailedResponse:
        status_code = 404
        headers = {"Content-Type": "text/html"}

        def raise_for_status(self):
            raise requests.HTTPError("404")

        def close(self):
            pass

    class Source:
        @staticmethod
        def get_download_links_from_detail(detail_url, timeout=120):
            return LinkInfo()

    monkeypatch.setattr(
        "src.link_to_file.requests.get",
        lambda *args, **kwargs: FailedResponse(),
    )
    link = Link_to_file("failed.bin", "https://example.test/detail", "1 B", Source)

    with pytest.raises(requests.RequestException):
        link.download(str(tmp_path))

    assert not (tmp_path / "failed.bin").exists()


def teardown_module():
    logger = logging.getLogger("universal_downloader")
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
