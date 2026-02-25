"""URL fetching tool backed by crawl4ai."""

from __future__ import annotations

import asyncio
import ipaddress
import socket
from typing import Any
from urllib.parse import urlparse

from langchain_core.tools import tool
from loguru import logger

_CRAWL_SEMAPHORE = asyncio.Semaphore(8)


def _is_internal_url(url: str) -> bool:
    """Return True if *url* resolves to a loopback or private network address."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""
    except Exception:
        return True

    if not hostname:
        return True

    _BLOCKED_HOSTS = {"localhost", "localhost.localdomain"}
    if hostname.lower() in _BLOCKED_HOSTS:
        return True

    try:
        addr = ipaddress.ip_address(hostname)
        return addr.is_loopback or addr.is_private or addr.is_reserved
    except ValueError:
        pass

    try:
        resolved = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
        for _, _, _, _, sockaddr in resolved:
            addr = ipaddress.ip_address(sockaddr[0])
            if addr.is_loopback or addr.is_private or addr.is_reserved:
                return True
    except (socket.gaierror, OSError):
        pass

    return False


async def _crawl_one(url: str) -> dict[str, Any]:
    """Crawl a single URL and return structured result dict."""
    try:
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        from crawl4ai.content_filter_strategy import PruningContentFilter
        from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
    except ImportError as exc:
        raise ImportError(
            "crawl4ai is required for web fetching. " "Install with: uv add crawl4ai"
        ) from exc

    prune_filter = PruningContentFilter(
        threshold=1.0,
        threshold_type="fixed",
        min_word_threshold=10,
    )
    md_generator = DefaultMarkdownGenerator(
        options={
            "ignore_links": True,
            "ignore_images": False,
            "escape_html": False,
        },
        content_filter=prune_filter,
    )
    config = CrawlerRunConfig(
        markdown_generator=md_generator,
        exclude_external_links=True,
        exclude_internal_links=True,
        exclude_social_media_links=True,
    )

    empty: dict[str, Any] = {
        "url": url,
        "title": "",
        "description": "",
        "content": "",
        "image_url": "",
    }

    async with _CRAWL_SEMAPHORE:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=url,
                config=config,
            )

    if not getattr(result, "success", False):
        logger.warning("Crawl failed for {}", url)
        return empty

    metadata = getattr(result, "metadata", {}) or {}
    raw_md = str(result.markdown.raw_markdown)
    fit_md = str(result.markdown.fit_markdown)
    stripped = fit_md.replace("\n", "").strip()
    content = fit_md if len(stripped) > 1 else raw_md

    image_url = (
        metadata.get(
            "og:image",
            metadata.get("twitter:image", ""),
        )
        or ""
    )
    title = (
        metadata.get(
            "title",
            metadata.get(
                "og:title",
                metadata.get("twitter:title", ""),
            ),
        )
        or ""
    )
    description = (
        metadata.get(
            "description",
            metadata.get(
                "og:description",
                metadata.get("twitter:description", ""),
            ),
        )
        or ""
    )

    return {
        "url": getattr(result, "url", url) or url,
        "title": title,
        "description": description,
        "content": content,
        "image_url": image_url,
    }


@tool
async def web_fetch(urls: list[str]) -> list[dict]:
    """Fetch content directly from specific URLs as markdown.

    Args:
        urls: List of complete URLs to fetch content from.
            Use when the user provides specific URLs they
            want to read or analyse.
    """
    logger.debug(
        "Fetching content from {} URLs: {}",
        len(urls),
        urls,
    )
    safe_urls: list[str] = []
    blocked: list[dict] = []
    for u in urls:
        if _is_internal_url(u):
            logger.warning("Blocked internal/private URL: {}", u)
            blocked.append({
                "url": u,
                "error": "Blocked: internal or private network addresses are not allowed.",
            })
        else:
            safe_urls.append(u)

    tasks = [_crawl_one(u) for u in safe_urls]
    results = await asyncio.gather(
        *tasks,
        return_exceptions=True,
    )

    output: list[dict] = list(blocked)
    for url, res in zip(safe_urls, results):
        if isinstance(res, Exception):
            logger.error("Error fetching {}: {}", url, res)
            output.append(
                {
                    "url": url,
                    "title": "",
                    "description": "",
                    "content": "",
                    "image_url": "",
                }
            )
        else:
            output.append(res)

    logger.debug("Fetch returned {} results", len(output))
    return output
