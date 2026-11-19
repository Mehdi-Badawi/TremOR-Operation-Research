import hashlib
import io
import json

import pytest

from tremor_screen import datasets

_PAYLOAD = b"mock impact-echo file"
_URL = "https://example.org/impact.zip"
_FILES_URL = (
    "https://data.mendeley.com/public-api/datasets/44rb96872r/files"
    "?folder_id=52975a8c-c538-49b5-9b6c-e234ced44d8f&version=1&$start=0&$limit=1000"
)


@pytest.fixture
def source(monkeypatch, tmp_path):
    digest = hashlib.sha256(_PAYLOAD).hexdigest()
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    monkeypatch.setattr(datasets, "_SHA256", digest)
    files = [{
        "filename": "BareAnnotated.zip",
        "content_details": {"sha256_hash": digest, "download_url": _URL},
    }]
    downloads = []
    requests = []

    def open_url(request, *, timeout):
        requests.append(request.full_url)
        assert request.get_header("User-agent", "").startswith("Mozilla/5.0")
        if request.full_url == _FILES_URL:
            assert request.get_header("Accept") == "application/vnd.mendeley-public-dataset.1+json"
            return io.BytesIO(json.dumps(files).encode())
        assert request.full_url == _URL
        assert timeout > 30
        return io.BytesIO(downloads.pop(0))

    monkeypatch.setattr(datasets, "urlopen", open_url)
    return files, downloads, requests


def test_load_reuses_verified_cache_and_replaces_corrupt_copy(source, tmp_path):
    _, downloads, requests = source
    downloads.append(_PAYLOAD)
    (path,) = datasets.load_bare_decks()
    assert path.is_relative_to(tmp_path / "tremor-screen")
    assert path.read_bytes() == _PAYLOAD
    assert datasets.load_bare_decks() == (path,)
    assert requests == [_FILES_URL, _URL]

    path.write_bytes(b"corrupt")
    downloads.append(_PAYLOAD)
    assert datasets.load_bare_decks() == (path,)
    assert path.read_bytes() == _PAYLOAD
    assert requests == [_FILES_URL, _URL, _FILES_URL, _URL]


def test_load_rejects_checksum_mismatch_without_caching(source, tmp_path):
    _, downloads, _ = source
    downloads.append(b"wrong bytes")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        datasets.load_bare_decks()
    assert not any(path.is_file() for path in tmp_path.rglob("*"))


@pytest.mark.parametrize(("field", "value", "message"), [
    ("filename", "../BareAnnotated.zip", "Invalid dataset filename"),
    ("sha256_hash", None, "Missing or invalid SHA-256"),
    ("sha256_hash", "bad", "Missing or invalid SHA-256"),
    ("sha256_hash", "0" * 64, "Unexpected published SHA-256"),
    ("download_url", "http://example.org/impact.zip", "Expected an HTTPS download URL"),
])
def test_load_rejects_invalid_file_metadata(source, field, value, message):
    files, _, requests = source
    entry = files[0] if field == "filename" else files[0]["content_details"]
    if value is None:
        del entry[field]
    else:
        entry[field] = value
    with pytest.raises(ValueError, match=message):
        datasets.load_bare_decks()
    assert requests == [_FILES_URL]


def test_load_rejects_empty_file_listing(source):
    files, _, requests = source
    files.clear()
    with pytest.raises(ValueError, match="Expected one archive"):
        datasets.load_bare_decks()
    assert requests == [_FILES_URL]
