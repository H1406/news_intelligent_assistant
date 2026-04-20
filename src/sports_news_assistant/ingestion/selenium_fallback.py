from __future__ import annotations

from contextlib import suppress


def fetch_article_with_selenium(url: str) -> str:
    try:
        from bs4 import BeautifulSoup
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
    except ImportError as exc:
        raise RuntimeError("Selenium fallback is not installed.") from exc

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )

    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p") if len(p.get_text(" ", strip=True)) >= 50]
        return "\n".join(paragraphs[:20])
    finally:
        with suppress(Exception):
            driver.quit()
