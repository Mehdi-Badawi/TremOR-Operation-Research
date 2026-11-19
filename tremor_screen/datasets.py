"""Download published concrete impact-echo data on demand."""

import hashlib
import json
import os
import re
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.request import Request, urlopen

_RECORD = "44rb96872r"
_FILES = (
    f"https://data.mendeley.com/public-api/datasets/{_RECORD}/files"
    "?folder_id=52975a8c-c538-49b5-9b6c-e234ced44d8f&version=1&$start=0&$limit=1000"
)
_USER_AGENT = "Mozilla/5.0 (compatible; tremor-screen/0.1)"
_SHA256 = "63f47047acc50b70079839c571886bb91ac90efcf1cdc14225afe4e5ec6beafc"
_CHUNK_SIZE = 1024 * 1024


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(_CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_bare_decks() -> tuple[Path, ...]:
    """Return verified local paths for Annotated Impact Echo Dataset (bare decks), v1."""
    cache_home = os.environ.get("XDG_CACHE_HOME")
    cache = Path(cache_home) if cache_home and Path(cache_home).is_absolute() else (
        Path.home() / ".cache"
    )
    cache = cache / "tremor-screen" / f"{_RECORD}.1"

    name = "BareAnnotated.zip"
    path = cache / _SHA256 / name
    if path.is_file() and _sha256(path) == _SHA256:
        return (path,)

    request = Request(_FILES, headers={
        "User-Agent": _USER_AGENT,
        "Accept": "application/vnd.mendeley-public-dataset.1+json",
    })
    with urlopen(request, timeout=30) as response:
        files = json.load(response)
    if not isinstance(files, list) or len(files) != 1:
        raise ValueError("Expected one archive in the version 1 Mendeley file listing")

    entry = files[0]
    if entry["filename"] != name:
        raise ValueError(f"Invalid dataset filename {entry['filename']!r}")
    details = entry["content_details"]
    expected = details.get("sha256_hash")
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
        raise ValueError(f"Missing or invalid SHA-256 for {name!r}")
    if expected.lower() != _SHA256:
        raise ValueError(f"Unexpected published SHA-256 for {name!r}")
    url = details.get("download_url")
    if not isinstance(url, str) or not url.startswith("https://"):
        raise ValueError(f"Expected an HTTPS download URL for {name!r}")

    path.parent.mkdir(parents=True, exist_ok=True)
    download = Request(url, headers={"User-Agent": _USER_AGENT})
    temporary = None
    try:
        with urlopen(download, timeout=120) as response:
            with NamedTemporaryFile(dir=path.parent, delete=False) as output:
                temporary = Path(output.name)
                for chunk in iter(lambda: response.read(_CHUNK_SIZE), b""):
                    output.write(chunk)
        if _sha256(temporary) != _SHA256:
            raise ValueError(f"SHA-256 mismatch for {name!r}")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return (path,)
