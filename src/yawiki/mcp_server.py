"""
Yandex Wiki MCP Server

MCP server exposing Yandex Wiki CRUD operations.
"""

import os
from typing import Optional

from fastmcp import FastMCP
from dotenv import load_dotenv

from yawiki.client import YandexWikiClient, WikiPage

load_dotenv()

mcp = FastMCP("yandex-wiki")

# Global client instance
_client: Optional[YandexWikiClient] = None


def get_client() -> YandexWikiClient:
    """Get or create the YandexWiki client."""
    global _client
    if _client is None:
        _client = YandexWikiClient()
    return _client


def _format_page(page: WikiPage) -> str:
    """Format a WikiPage for display."""
    result = f"ID: {page.id}\n"
    result += f"Slug: {page.slug}\n"
    result += f"Title: {page.title}\n"
    result += f"Type: {page.page_type}"
    if page.content:
        result += f"\n\n--- Content ---\n{page.content}"
    return result


@mcp.tool()
def wiki_create(page_path: str, title: str, content: str = "") -> str:
    """
    Create a new Yandex Wiki page.

    Args:
        page_path: Path relative to YANDEX_WIKI_BASE_SLUG (e.g., "scenarios/analytics/US-AN-001")
        title: Page title
        content: Page content in Markdown (optional)

    Returns:
        Created page information
    """
    client = get_client()
    page = client.create(page_path, title, content)
    return f"Created page:\n{_format_page(page)}"


@mcp.tool()
def wiki_read(page_path: str, include_content: bool = True) -> str:
    """
    Read a Yandex Wiki page.

    Args:
        page_path: Path relative to YANDEX_WIKI_BASE_SLUG
        include_content: Whether to include page content (default: True)

    Returns:
        Page information including content
    """
    client = get_client()
    page = client.read(page_path, include_content=include_content)
    return _format_page(page)


@mcp.tool()
def wiki_update(page_path: str, title: Optional[str] = None, content: Optional[str] = None) -> str:
    """
    Update a Yandex Wiki page.

    Args:
        page_path: Path relative to YANDEX_WIKI_BASE_SLUG
        title: New title (optional)
        content: New content in Markdown (optional)

    Returns:
        Updated page information
    """
    client = get_client()
    page = client.update(page_path, title=title, content=content)
    return f"Updated page:\n{_format_page(page)}"


@mcp.tool()
def wiki_delete(page_path: str) -> str:
    """
    Delete a Yandex Wiki page.

    Args:
        page_path: Path relative to YANDEX_WIKI_BASE_SLUG

    Returns:
        Confirmation message
    """
    client = get_client()
    client.delete(page_path)
    return f"Deleted page: {client.base_slug}/{page_path}"


@mcp.tool()
def wiki_exists(page_path: str) -> str:
    """
    Check if a Yandex Wiki page exists.

    Args:
        page_path: Path relative to YANDEX_WIKI_BASE_SLUG

    Returns:
        Whether the page exists
    """
    client = get_client()
    exists = client.exists(page_path)
    return f"Page {client.base_slug}/{page_path} exists: {exists}"


@mcp.tool()
def wiki_get_or_create(page_path: str, title: str, content: str = "") -> str:
    """
    Get an existing page or create a new one if it doesn't exist.

    Args:
        page_path: Path relative to YANDEX_WIKI_BASE_SLUG
        title: Page title (used if creating)
        content: Page content in Markdown (used if creating)

    Returns:
        Page information and whether it was created
    """
    client = get_client()
    page, created = client.get_or_create(page_path, title, content)
    status = "Created new page" if created else "Found existing page"
    return f"{status}:\n{_format_page(page)}"


if __name__ == "__main__":
    mcp.run()
