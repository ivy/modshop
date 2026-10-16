"""The mod archives: how their folders are named, and the downloaders that fetch them.

`fetch_build` walks the build's mod list (`k1full.json`) and fetches each mod's files into
`<archives>/NNN-<slug>/`: DeadlyStream as a guest (multi-file pages use the picks below), Nexus
through its API with a premium key. mega.nz links are fetched by `fetch_mega`. The picks are the
file ids chosen on each site's page for mods that offer several downloads.
"""

from __future__ import annotations

import base64
import html
import http.cookiejar
import json
import logging
import re
import struct
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

log = logging.getLogger("modshop")


def slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def folder_name(number: int, title: str) -> str:
    """The archive folder for the build's mod number `number`: `NNN-<slug>`."""
    return f"{number:03d}-{slug(title)}"


# ---- the build's sites ---------------------------------------------------------------------------

DS_PICKS: dict[str, list[str]] = {
    "1258": ["85513", "85516"], "2514": ["85520"], "980": ["85214"], "1909": ["53226"], "1213": ["46015"],
    "2516": ["83986", "83987"], "2277": ["70859"], "2430": ["78365"], "2382": ["84585"], "1133": ["85268"],
    "2031": ["84597"], "1929": ["54734"], "1125": ["86160"], "723": ["53694"], "1925": ["85281"], "2522": ["72769"],
    "2739": ["84640"], "1199": ["71059"], "2659": ["75302"],
}  # fmt: skip
NX_PICKS: dict[str, list[int]] = {
    "1367": [2204], "1365": [2217], "1364": [2213], "1368": [2223], "1370": [2225], "1366": [2221], "1360": [2211],
    "1282": [1968, 1973, 1974, 1975, 1976, 1977, 1978], "1369": [2302], "1632": [2606, 2608], "1209": [1588],
    "1192": [1546], "90": [145], "1666": [2722], "1710": [2900], "1711": [3008], "66": [77], "1384": [1933],
}  # fmt: skip
USER_AGENT = "Mozilla/5.0"


def _opener() -> urllib.request.OpenerDirector:
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    op.addheaders = [("User-Agent", USER_AGENT)]
    return op


def _save(resp: Any, dest: Path, fallback: str) -> None:
    cd = resp.headers.get("Content-Disposition", "")
    m = re.search(r"filename\*=UTF-8''([^;]+)", cd) or re.search(r'filename="?([^";]+)"?', cd)
    name = urllib.parse.unquote(m.group(1)) if m else ""
    if not m:
        name = Path(urllib.parse.unquote(resp.geturl().split("?")[0])).name or fallback
    name = Path(name.replace("\\", "/")).name
    p = dest / name
    if p.exists() and p.stat().st_size > 0:
        log.info("  have %s", name)
        return
    tmp = p.with_suffix(p.suffix + ".part")
    with tmp.open("wb") as f:
        while True:
            b = resp.read(1 << 20)
            if not b:
                break
            f.write(b)
    tmp.rename(p)
    log.info("  got %s %d", name, p.stat().st_size)


def fetch_build(k1full: Path, archives: Path, nexus_key: str) -> None:
    mods = json.loads(k1full.read_text())
    op = _opener()
    archives.mkdir(parents=True, exist_ok=True)
    n = 0
    for m in mods:
        if m["section"] != "Mod List":
            continue
        n += 1
        dest = archives / folder_name(n, m["title"])
        dest.mkdir(exist_ok=True)
        log.info("[%d] %s", n, m["title"])
        for link in m.get("links", []):
            try:
                _fetch_link(op, link, dest, nexus_key)
            except Exception as e:
                log.error("  ERROR %s %s", link, e)
            time.sleep(0.5)
    log.info("DONE")


def _fetch_link(op: urllib.request.OpenerDirector, link: str, dest: Path, nexus_key: str) -> None:
    dm = re.match(r"https?://deadlystream\.com/files/file/(\d+)-[^/?#]+", link)
    nm = re.match(r"https://www\.nexusmods\.com/kotor/mods/(\d+)", link)
    if dm:
        fid, base = dm.group(1), dm.group(0) + "/"
        if fid in DS_PICKS:
            page = op.open(base + "?do=download", timeout=120).read().decode("utf-8", "replace")
            for r in DS_PICKS[fid]:
                hm = re.search(r"""href=["']([^"']*r=""" + re.escape(r) + r"""[^"']*)["']""", page)
                if not hm:
                    log.warning("  MISSING r=%s", r)
                    continue
                _save(op.open(html.unescape(hm.group(1)), timeout=600), dest, f"ds{fid}-{r}.bin")
        else:
            resp = op.open(base + "?do=download", timeout=600)
            if "text/html" in resp.headers.get("Content-Type", ""):
                page = resp.read().decode("utf-8", "replace")
                hm = re.search(r"""href=["']([^"']*do=download[^"']*csrfKey=[^"']*)["']""", page)
                if not hm:
                    log.warning("  no download link on %s", base)
                    return
                resp = op.open(html.unescape(hm.group(1)), timeout=600)
            _save(resp, dest, f"ds{fid}.bin")
    elif nm:
        mid = nm.group(1)
        if mid not in NX_PICKS:
            log.warning("  no nexus pick for %s", mid)
            return
        for fid in NX_PICKS[mid]:
            req = urllib.request.Request(
                f"https://api.nexusmods.com/v1/games/kotor/mods/{mid}/files/{fid}/download_link.json",
                headers={"apikey": nexus_key, "accept": "application/json"},
            )
            links = json.load(urllib.request.urlopen(req, timeout=60))
            url = links[0]["URI"].replace(" ", "%20")
            _save(op.open(url, timeout=1200), dest, f"nexus{mid}-{fid}.bin")
    else:
        log.info("  other host: %s", link)


# ---- mega.nz ------------------------------------------------------------------------------------


def _b64d(s: str) -> bytes:
    s = s.replace("-", "+").replace("_", "/")
    return base64.b64decode(s + "=" * (-len(s) % 4))


def _words(b: bytes) -> tuple[int, ...]:
    return struct.unpack(f">{len(b) // 4}I", b)


def _mega_api(req: dict[str, object]) -> Any:
    r = urllib.request.Request(
        "https://g.api.mega.co.nz/cs?id=1",
        data=json.dumps([req]).encode(),
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
    )
    return json.load(urllib.request.urlopen(r, timeout=60))[0]


def mega_link(url: str) -> tuple[str, str]:
    """The file id and key of a public mega.nz link (new `file/ID#KEY` and old `#!ID!KEY` forms)."""
    m = re.search(r"mega\.nz/(?:file/([^#]+)#([^ ]+)|#!([^!]+)!([^ ]+))", url)
    if not m:
        raise ValueError(f"not a mega.nz file link: {url}")
    return (m.group(1) or m.group(3)), (m.group(2) or m.group(4))


def fetch_mega(url: str, dest: Path) -> Path:
    from Crypto.Cipher import AES  # pyright: ignore[reportMissingTypeStubs]
    from Crypto.Util import Counter  # pyright: ignore[reportMissingTypeStubs]

    fid, key = mega_link(url)
    k = _words(_b64d(key))
    fk = struct.pack(">4I", k[0] ^ k[4], k[1] ^ k[5], k[2] ^ k[6], k[3] ^ k[7])
    iv = (k[4] << 32 | k[5]) << 64
    info = _mega_api({"a": "g", "g": 1, "p": fid})
    if isinstance(info, int):
        raise RuntimeError(f"mega error {info}")
    attrs = AES.new(fk, AES.MODE_CBC, b"\0" * 16).decrypt(_b64d(info["at"])).rstrip(b"\0")
    name = json.loads(attrs[4:].decode())["n"]
    size = info["s"]
    p = dest / name
    if p.exists() and p.stat().st_size == size:
        log.info("have %s %d", name, size)
        return p
    c = AES.new(fk, AES.MODE_CTR, counter=Counter.new(128, initial_value=iv))
    req = urllib.request.Request(info["g"], headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=600) as r, p.open("wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(c.decrypt(b))
    log.info("got %s %d %d", name, size, p.stat().st_size)
    return p
