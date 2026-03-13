"""
Article Content Scraper Service (async)

Scrapes article content using newspaper3k → BeautifulSoup fallback.
Uses httpx for async HTTP requests (no Django/requests dependency).
"""

import logging
from typing import Tuple

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False

MAX_CONTENT_LENGTH = 3000
REQUEST_TIMEOUT = 10
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/91.0.4472.124 Safari/537.36"
)


async def scrape_article(article_url: str) -> Tuple[str, str]:
    """
    Scrape article content from URL. Returns (title, content).
    Raises Exception if scraping fails.
    """
    # Method 1: newspaper3k (sync, run in threadpool via asyncio)
    if NEWSPAPER_AVAILABLE:
        try:
            import asyncio
            title, content = await asyncio.get_event_loop().run_in_executor(
                None, _scrape_with_newspaper, article_url
            )
            if content and len(content.strip()) > 100:
                logger.info(
                    "[ARTICLE_SCRAPER] newspaper3k success: '%s...' (%d chars)",
                    title[:50],
                    len(content),
                )
                return _process_content(title, content)
        except Exception as exc:
            logger.warning("[ARTICLE_SCRAPER] newspaper3k failed: %s", exc)

    # Method 2: httpx + BeautifulSoup
    try:
        title, content = await _scrape_with_httpx(article_url)
        if content and len(content.strip()) > 100:
            logger.info(
                "[ARTICLE_SCRAPER] BeautifulSoup success: '%s...' (%d chars)",
                title[:50],
                len(content),
            )
            return _process_content(title, content)
        raise Exception("Insufficient content extracted")
    except Exception as exc:
        logger.error("[ARTICLE_SCRAPER] All methods failed: %s", exc)
        raise Exception(
            "Unable to fetch article content. "
            "Please try a different URL or use a text description instead."
        ) from None


def _scrape_with_newspaper(article_url: str) -> Tuple[str, str]:
    article = Article(article_url)
    article.download()
    article.parse()
    return article.title or "Article Content", article.text or ""


async def _scrape_with_httpx(article_url: str) -> Tuple[str, str]:
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
        resp = await client.get(article_url, headers=headers)
        resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "html.parser")
    title = _extract_title(soup)
    content = _extract_content(soup)
    return title, content


def _extract_title(soup: BeautifulSoup) -> str:
    for tag in [
        soup.find("h1"),
        soup.find("title"),
        soup.find("meta", property="og:title"),
        soup.find("meta", attrs={"name": "title"}),
    ]:
        if tag:
            text = tag.get("content", "").strip() if tag.name == "meta" else tag.get_text().strip()
            if text:
                return text
    return "Article Content"


def _extract_content(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "iframe"]):
        tag.decompose()

    for tag_name, class_filter in [
        ("article", None),
        ("main", None),
        ("div", lambda x: x and any(k in str(x).lower() for k in ["content", "article", "post-body", "entry-content", "story-body"])),
    ]:
        areas = soup.find_all(tag_name, class_=class_filter) if class_filter else soup.find_all(tag_name)
        if areas:
            text = areas[0].get_text(separator=" ", strip=True)
            if len(text) > 100:
                return _clean_text(text)

    paragraphs = soup.find_all("p")
    return _clean_text(" ".join(p.get_text(strip=True) for p in paragraphs))


def _clean_text(text: str) -> str:
    return " ".join(text.split())


def _process_content(title: str, content: str) -> Tuple[str, str]:
    if len(content) > MAX_CONTENT_LENGTH:
        content = content[:MAX_CONTENT_LENGTH] + "... (content truncated)"
    return title, content
