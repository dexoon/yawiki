"""
Yandex Wiki API Client

CRUD operations for Yandex Wiki pages.
Base path is configurable via YANDEX_WIKI_BASE_SLUG environment variable.
"""

import os
import json
from typing import Optional
from dataclasses import dataclass
from functools import cached_property

import requests
from dotenv import load_dotenv


load_dotenv()


@dataclass
class WikiPage:
    """Represents a Yandex Wiki page."""
    id: int
    slug: str
    title: str
    page_type: str
    content: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "WikiPage":
        return cls(
            id=data["id"],
            slug=data["slug"],
            title=data["title"],
            page_type=data["page_type"],
            content=data.get("content"),
        )

    def to_dict(self) -> dict:
        result = {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "page_type": self.page_type,
        }
        if self.content is not None:
            result["content"] = self.content
        return result


class YandexWikiClient:
    """Client for Yandex Wiki API."""

    BASE_URL = "https://api.wiki.yandex.net/v1"

    def __init__(
        self,
        token: Optional[str] = None,
        org_id: Optional[str] = None,
        base_slug: Optional[str] = None,
    ):
        self.token = token or os.getenv("YANDEX_WIKI_TOKEN")
        self.org_id = org_id or os.getenv("YANDEX_TRACKER_ORG_ID")
        self.base_slug = base_slug or os.getenv("YANDEX_WIKI_BASE_SLUG")

        if not self.token:
            raise ValueError("YANDEX_WIKI_TOKEN is required")
        if not self.org_id:
            raise ValueError("YANDEX_TRACKER_ORG_ID is required")

    @cached_property
    def headers(self) -> dict:
        return {
            "Authorization": f"OAuth {self.token}",
            "X-Org-Id": self.org_id,
            "Content-Type": "application/json",
        }

    def _make_slug(self, page_path: str) -> str:
        """
        Convert page path to full slug.

        Examples:
            "mypage" -> "{base_slug}/mypage"
            "scenarios/analytics/US-AN-001" -> "{base_slug}/scenarios/analytics/US-AN-001"
        """
        # Remove leading slash if present
        page_path = page_path.lstrip("/")
        # Remove base_slug prefix if already present
        if page_path.startswith(self.base_slug):
            page_path = page_path[len(self.base_slug):].lstrip("/")
        return f"{self.base_slug}/{page_path}"

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> dict:
        """Make HTTP request to API."""
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            params=params,
            json=data,
        )
        response.raise_for_status()
        return response.json()

    # ==================== CRUD Operations ====================

    def create(
        self,
        page_path: str,
        title: str,
        content: str = "",
        page_type: str = "wysiwyg",
    ) -> WikiPage:
        """
        Create a new page.

        Args:
            page_path: Path relative to base_slug (e.g., "scenarios/analytics/US-AN-001")
            title: Page title
            content: Page content in Markdown
            page_type: Page type (page, grid, wysiwyg, etc.)

        Returns:
            Created WikiPage object
        """
        slug = self._make_slug(page_path)
        data = {
            "slug": slug,
            "title": title,
            "content": content,
            "page_type": page_type,
        }
        result = self._request("POST", "/pages", data=data)
        return WikiPage.from_dict(result)

    def read(self, page_path: str, include_content: bool = True) -> WikiPage:
        """
        Read a page by path.

        Args:
            page_path: Path relative to base_slug
            include_content: Whether to include page content

        Returns:
            WikiPage object
        """
        slug = self._make_slug(page_path)
        params = {"slug": slug}
        if include_content:
            params["fields"] = "content"
        result = self._request("GET", "/pages", params=params)
        return WikiPage.from_dict(result)

    def update(
        self,
        page_path: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
    ) -> WikiPage:
        """
        Update a page.

        Args:
            page_path: Path relative to base_slug
            title: New title (optional)
            content: New content (optional)

        Returns:
            Updated WikiPage object
        """
        slug = self._make_slug(page_path)
        data = {}
        if title is not None:
            data["title"] = title
        if content is not None:
            data["content"] = content

        # PATCH request with slug in query params
        params = {"slug": slug}
        result = self._request("PATCH", "/pages", params=params, data=data)
        return WikiPage.from_dict(result)

    def delete(self, page_path: str) -> bool:
        """
        Delete a page.

        Args:
            page_path: Path relative to base_slug

        Returns:
            True if deleted successfully
        """
        # First get the page ID using slug
        page = self.read(page_path, include_content=False)
        # Then delete by ID
        self._request("DELETE", f"/pages/{page.id}")
        return True

    # ==================== Convenience Methods ====================

    def exists(self, page_path: str) -> bool:
        """Check if a page exists."""
        try:
            self.read(page_path, include_content=False)
            return True
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return False
            raise

    def get_or_create(
        self,
        page_path: str,
        title: str,
        content: str = "",
    ) -> tuple[WikiPage, bool]:
        """
        Get existing page or create new one.

        Returns:
            Tuple of (WikiPage, created) where created is True if page was created
        """
        try:
            page = self.read(page_path)
            return page, False
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                page = self.create(page_path, title, content)
                return page, True
            raise


# ==================== CLI Interface ====================

def main():
    """Command-line interface for Yandex Wiki CRUD operations."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Yandex Wiki CRUD operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a page
  python yawiki_client.py create scenarios/test "Test Page" -c "# Content"

  # Read a page
  python yawiki_client.py read scenarios/test

  # Update a page
  python yawiki_client.py update scenarios/test -t "New Title" -c "New content"

  # Delete a page
  python yawiki_client.py delete scenarios/test

  # Check if page exists
  python yawiki_client.py exists scenarios/test
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new page")
    create_parser.add_argument("path", help="Page path (e.g., scenarios/test)")
    create_parser.add_argument("title", help="Page title")
    create_parser.add_argument("-c", "--content", default="", help="Page content")
    create_parser.add_argument("-t", "--type", default="wysiwyg", help="Page type")

    # Read command
    read_parser = subparsers.add_parser("read", help="Read a page")
    read_parser.add_argument("path", help="Page path")
    read_parser.add_argument("--no-content", action="store_true", help="Don't include content")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update a page")
    update_parser.add_argument("path", help="Page path")
    update_parser.add_argument("-t", "--title", help="New title")
    update_parser.add_argument("-c", "--content", help="New content")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a page")
    delete_parser.add_argument("path", help="Page path")

    # Exists command
    exists_parser = subparsers.add_parser("exists", help="Check if page exists")
    exists_parser.add_argument("path", help="Page path")

    args = parser.parse_args()

    client = YandexWikiClient()

    if args.command == "create":
        page = client.create(args.path, args.title, args.content, args.type)
        print(f"Created: {page.slug} (ID: {page.id})")

    elif args.command == "read":
        page = client.read(args.path, include_content=not args.no_content)
        print(json.dumps(page.to_dict(), indent=2, ensure_ascii=False))

    elif args.command == "update":
        page = client.update(args.path, title=args.title, content=args.content)
        print(f"Updated: {page.slug}")

    elif args.command == "delete":
        client.delete(args.path)
        print(f"Deleted: {args.path}")

    elif args.command == "exists":
        exists = client.exists(args.path)
        print(f"Exists: {exists}")


if __name__ == "__main__":
    main()
