from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import fitz
from bs4 import BeautifulSoup
from markdown_it import MarkdownIt


@dataclass(frozen=True)
class ParsedPage:
    document_name: str
    document_type: str
    page_number: int
    text: str


def parse_pdf(path: str | Path) -> list[ParsedPage]:
    document_path = Path(path)
    pages: list[ParsedPage] = []

    with fitz.open(document_path) as document:
        for page_index, page in enumerate(document, start=1):
            pages.append(
                ParsedPage(
                    document_name=document_path.name,
                    document_type="pdf",
                    page_number=page_index,
                    text=page.get_text().strip(),
                )
            )

    return pages


def parse_html(path: str | Path) -> list[ParsedPage]:
    document_path = Path(path)
    html = document_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    return [_single_page(document_path, "html", text)]


def parse_markdown(path: str | Path) -> list[ParsedPage]:
    document_path = Path(path)
    markdown = document_path.read_text(encoding="utf-8")
    tokens = MarkdownIt().parse(markdown)
    text = "\n".join(_token_text(tokens)).strip()

    return [_single_page(document_path, "markdown", text)]


def parse_document(path: str | Path) -> list[ParsedPage]:
    document_path = Path(path)
    suffix = document_path.suffix.lower()

    if suffix == ".pdf":
        return parse_pdf(document_path)
    if suffix in {".html", ".htm"}:
        return parse_html(document_path)
    if suffix in {".md", ".markdown"}:
        return parse_markdown(document_path)

    raise ValueError(f"Unsupported document type: {document_path.suffix}")


def _single_page(document_path: Path, document_type: str, text: str) -> ParsedPage:
    return ParsedPage(
        document_name=document_path.name,
        document_type=document_type,
        page_number=1,
        text=text.strip(),
    )


def _token_text(tokens: Iterable) -> Iterable[str]:
    for token in tokens:
        if token.type in {"inline", "code_block", "fence", "html_block"} and token.content:
            yield token.content.strip()
