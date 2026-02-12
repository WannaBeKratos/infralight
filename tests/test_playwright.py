"""Playwright E2E tests for Infralight.

Tests all pages load, navigation works, and key UI elements are present.
"""

from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page, expect

# ── Helpers ──────────────────────────────────────────────────────


def _go(page: Page, base_url: str, path: str = "/") -> None:
    """Navigate and wait for the NiceGUI app to be ready."""
    page.goto(f"{base_url}{path}")
    # Wait for the NiceGUI-generated content to appear
    page.wait_for_selector(".q-layout", timeout=10_000)


# ── Layout & navigation ─────────────────────────────────────────


class TestLayout:
    """Header, sidebar, and navigation structure."""

    def test_header_visible(self, page: Page, base_url: str) -> None:
        _go(page, base_url)
        header = page.locator("header")
        expect(header).to_be_visible()
        expect(header).to_contain_text("Infralight")

    def test_sidebar_nav_items(self, page: Page, base_url: str) -> None:
        _go(page, base_url)
        sidebar = page.locator(".q-drawer")
        expect(sidebar).to_be_visible()
        for label in [
            "Dashboard",
            "Salt States",
            "Salt Overview",
            "TF Resources",
            "Visualization",
            "File Editor",
            "Render Output",
        ]:
            expect(sidebar.get_by_text(label, exact=True)).to_be_visible()

    def test_sidebar_file_tree(self, page: Page, base_url: str) -> None:
        _go(page, base_url)
        expect(page.get_by_text("FILES", exact=True)).to_be_visible()

    def test_sidebar_project_info(self, page: Page, base_url: str) -> None:
        _go(page, base_url)
        sidebar = page.locator(".q-drawer")
        expect(sidebar.get_by_text("files", exact=False).first).to_be_visible()

    def test_sidebar_navigate_to_states(self, page: Page, base_url: str) -> None:
        _go(page, base_url)
        page.locator(".q-drawer").get_by_text("Salt States", exact=True).click()
        page.wait_for_url(re.compile(r"/states"))
        expect(page.locator("body")).to_contain_text("Salt States")


# ── Dashboard ────────────────────────────────────────────────────


class TestDashboard:
    """Dashboard page tests."""

    def test_loads(self, page: Page, base_url: str) -> None:
        _go(page, base_url)
        expect(page.locator("body")).to_contain_text("Dashboard")

    def test_stat_cards(self, page: Page, base_url: str) -> None:
        _go(page, base_url)
        for label in [
            "Files",
            "Salt States",
            "TF Resources",
            "IL Templates",
            "Resources",
        ]:
            expect(page.get_by_text(label).first).to_be_visible()

    def test_issues_panel(self, page: Page, base_url: str) -> None:
        _go(page, base_url)
        expect(page.get_by_text("Issues")).to_be_visible()

    def test_project_files_panel(self, page: Page, base_url: str) -> None:
        _go(page, base_url)
        # The project files panel should be present
        expect(page.get_by_text("Project Files")).to_be_visible()


# ── Salt States ──────────────────────────────────────────────────


class TestSaltStates:
    """Salt States page tests."""

    def test_loads(self, page: Page, base_url: str) -> None:
        _go(page, base_url, "/states")
        expect(page.locator("body")).to_contain_text("Salt States")

    def test_table_has_rows(self, page: Page, base_url: str) -> None:
        _go(page, base_url, "/states")
        rows = page.locator("table tbody tr")
        expect(rows.first).to_be_visible()

    def test_table_columns(self, page: Page, base_url: str) -> None:
        _go(page, base_url, "/states")
        for col in ["File", "Path", "Kind", "States", "Modules"]:
            expect(page.get_by_text(col).first).to_be_visible()


# ── Salt Overview ────────────────────────────────────────────────


class TestSaltOverview:
    """Salt Overview page tests."""

    def test_loads(self, page: Page, base_url: str) -> None:
        _go(page, base_url, "/salt-overview")
        expect(page.locator("body")).to_contain_text("Total States")

    def test_category_panels(self, page: Page, base_url: str) -> None:
        _go(page, base_url, "/salt-overview")
        # At least one category should appear (Packages, Services, Files, etc.)
        expect(page.get_by_text("Packages").first).to_be_visible()


# ── TF Resources ─────────────────────────────────────────────────


class TestResources:
    """Terraform Resources page tests."""

    def test_loads(self, page: Page, base_url: str) -> None:
        _go(page, base_url, "/resources")
        # Should show the resources panel
        expect(page.locator("body")).to_contain_text("Resources")

    def test_table_has_rows(self, page: Page, base_url: str) -> None:
        _go(page, base_url, "/resources")
        rows = page.locator("table tbody tr")
        expect(rows.first).to_be_visible()


# ── Visualization ────────────────────────────────────────────────


class TestVisualization:
    """Visualization page tests."""

    def test_loads(self, page: Page, base_url: str) -> None:
        _go(page, base_url, "/visualization")
        expect(page.locator("body")).to_contain_text("Combined")

    def test_three_tabs(self, page: Page, base_url: str) -> None:
        _go(page, base_url, "/visualization")
        for tab_label in ["Combined", "Infrastructure", "IL Decorators"]:
            expect(page.get_by_text(tab_label).first).to_be_visible()

    def test_zoom_controls(self, page: Page, base_url: str) -> None:
        _go(page, base_url, "/visualization")
        # The zoom container with +/-/reset buttons is rendered via ui.html
        # Look for the reset button character (↺) as proof it rendered
        page.wait_for_timeout(3000)
        zoom_btn = page.locator("button[title='Zoom in']")
        expect(zoom_btn.first).to_be_attached(timeout=10_000)

    def test_tab_switch(self, page: Page, base_url: str) -> None:
        _go(page, base_url, "/visualization")
        page.get_by_text("Infrastructure", exact=True).click()
        expect(page.get_by_text("Infrastructure Graph")).to_be_visible()

    def test_node_edge_counts(self, page: Page, base_url: str) -> None:
        _go(page, base_url, "/visualization")
        # The stats line shows "X nodes · Y edges"
        expect(page.get_by_text("nodes").first).to_be_visible()
        expect(page.get_by_text("edges").first).to_be_visible()


# ── Render Output ────────────────────────────────────────────────


class TestOutput:
    """Render Output page tests."""

    def test_loads(self, page: Page, base_url: str) -> None:
        _go(page, base_url, "/output")
        expect(page.locator("body")).to_contain_text("Render")


# ── File Editor ──────────────────────────────────────────────────


class TestEditor:
    """File Editor page tests."""

    def test_loads(self, page: Page, base_url: str) -> None:
        _go(page, base_url, "/editor")
        expect(page.locator("body")).to_contain_text("Files")

    def test_file_tree_visible(self, page: Page, base_url: str) -> None:
        _go(page, base_url, "/editor")
        # Editor page has its own file tree — use the main content area tree
        tree = page.locator(".q-page .q-tree")
        expect(tree).to_be_visible()

    def test_open_file_via_query(self, page: Page, base_url: str) -> None:
        _go(page, base_url, "/editor?file=terraform/vpc.il.tf")
        # Should auto-open the file — check the editor panel shows content
        page.wait_for_timeout(1500)
        # The file name appears in the tree (may be hidden in scroll)
        # so check for it being attached to the DOM instead
        expect(page.get_by_text("vpc.il.tf").first).to_be_attached()

    def test_open_salt_file(self, page: Page, base_url: str) -> None:
        _go(page, base_url, "/editor?file=saltstack/common.sls")
        page.wait_for_timeout(1500)
        expect(page.get_by_text("common.sls").first).to_be_attached()


# ── Cross-page navigation ───────────────────────────────────────


class TestNavigation:
    """End-to-end navigation between pages."""

    @pytest.mark.parametrize(
        "nav_label,expected_url_part",
        [
            ("Dashboard", "/"),
            ("Salt States", "/states"),
            ("Salt Overview", "/salt-overview"),
            ("TF Resources", "/resources"),
            ("Visualization", "/visualization"),
            ("File Editor", "/editor"),
            ("Render Output", "/output"),
        ],
    )
    def test_nav_links(
        self, page: Page, base_url: str, nav_label: str, expected_url_part: str
    ) -> None:
        _go(page, base_url)
        page.locator(".q-drawer").get_by_text(nav_label, exact=True).click()
        if expected_url_part == "/":
            page.wait_for_url(re.compile(r"/$"))
        else:
            page.wait_for_url(re.compile(re.escape(expected_url_part)))
        expect(page.locator(".q-layout")).to_be_visible()
