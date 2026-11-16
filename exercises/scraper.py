"""Small, dependency-free helper for extracting readable text from a webpage."""

from html.parser import HTMLParser
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class _VisibleTextParser(HTMLParser):
    """Collect text while ignoring page chrome and non-visible elements."""

    _ignored_tags = {
        "script",
        "style",
        "nav",
        "header",
        "footer",
        "svg",
        "noscript",
    }

    def __init__(self) -> None:
        super().__init__()
        self._ignored_depth = 0
        self._title_depth = 0
        self.title: list[str] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in self._ignored_tags:
            self._ignored_depth += 1
        elif tag == "title":
            self._title_depth += 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self._ignored_tags and self._ignored_depth:
            self._ignored_depth -= 1
        elif tag == "title" and self._title_depth:
            self._title_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return

        cleaned = " ".join(data.split())
        if not cleaned:
            return

        if self._title_depth:
            self.title.append(cleaned)
        else:
            self.text.append(cleaned)


def fetch_website_contents(url: str) -> str:
    """Download *url* and return its title and visible text."""
    parsed_url = urlparse(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ValueError("URL must be a complete http:// or https:// address")

    request = Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; llm-pro/0.1)"},
    )
    with urlopen(request, timeout=15) as response:
        content_type = response.headers.get_content_type()
        if content_type not in {"text/html", "application/xhtml+xml"}:
            raise ValueError(f"Expected an HTML page, received {content_type}")

        charset = response.headers.get_content_charset() or "utf-8"
        html = response.read().decode(charset, errors="replace")

    parser = _VisibleTextParser()
    parser.feed(html)

    title = " ".join(parser.title)
    body = "\n".join(parser.text)
    return f"Title: {title}\n\n{body}" if title else body
