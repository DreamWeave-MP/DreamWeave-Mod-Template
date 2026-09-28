"""Check the built site's local links, assets and #fragments, including under a Pages subdirectory.

Adapted from StroggForge's scripts/war-room/check-site.py. External links are not fetched: whether
GitHub is up says nothing about whether this site is correct.
"""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


class Document(HTMLParser):
    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.feed(text)

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if tag in ("a", "link") and attributes.get("href"):
            self.links.append(attributes["href"])
        if tag in ("img", "script", "source") and attributes.get("src"):
            self.links.append(attributes["src"])


def check_site(public: Path, base_url: str) -> tuple[int, list[str]]:
    base = base_url.rstrip("/") + "/"
    base_parts = urlsplit(base)
    documents = {path: Document(path.read_text(encoding="utf-8")) for path in sorted(public.rglob("*.html"))}
    if not documents:
        return 0, [f"{public} has no HTML; run zola build first"]

    errors = []
    checked = 0
    for path, document in documents.items():
        relative = path.relative_to(public).as_posix()
        current = urljoin(base, relative.removesuffix("index.html"))
        for link in document.links:
            target = urlsplit(urljoin(current, link))
            if target.scheme not in ("http", "https") or target.netloc != base_parts.netloc:
                continue
            if not target.path.startswith(base_parts.path):
                if not urlsplit(link).netloc:
                    errors.append(f"{relative}: {link} escapes the site's base path {base_parts.path}")
                continue
            local = public / unquote(target.path[len(base_parts.path):])
            if local.is_dir():
                local /= "index.html"
            checked += 1
            if not local.is_file():
                errors.append(f"{relative}: missing target {link}")
            elif target.fragment and local.suffix == ".html" and unquote(target.fragment) not in documents[local].ids:
                errors.append(f"{relative}: missing anchor {link}")
    return checked, errors
