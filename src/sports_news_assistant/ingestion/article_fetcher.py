from __future__ import annotations

import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class ArticleFetcher:
    def __init__(self, timeout: int = 20) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
                )
            }
        )

    def fetch_article_text(self, url: str) -> str:
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        domain = urlparse(url).netloc
        selectors = _domain_selectors(domain)
        paragraphs: list[str] = []

        for selector in selectors:
            for node in soup.select(selector):
                text = _clean_text(node.get_text(" ", strip=True))
                if len(text) >= 50:
                    paragraphs.append(text)

        if not paragraphs:
            for node in soup.find_all(["p"]):
                text = _clean_text(node.get_text(" ", strip=True))
                if len(text) >= 50:
                    paragraphs.append(text)

        unique_paragraphs = list(dict.fromkeys(paragraphs))
        return "\n".join(unique_paragraphs[:20])


def _domain_selectors(domain: str) -> list[str]:
    if "vnexpress" in domain:
        return [".fck_detail p", "article p"]
    if "thanhnien" in domain:
        return [".detail-content p", ".cms-body p", "article p"]
    if "tuoitre" in domain:
        return [".detail-content p", ".content-fck p", "article p"]
    return ["article p", ".article-content p", ".detail-content p"]


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
